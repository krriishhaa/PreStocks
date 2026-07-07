import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from datetime import datetime, timedelta
from backend.data_sources import YFinanceSource

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

class LSTMForecaster(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1):
        super(LSTMForecaster, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

class MinMaxScale:
    def __init__(self):
        self.min_val = 0.0
        self.max_val = 1.0
        
    def fit_transform(self, data):
        self.min_val = np.min(data)
        self.max_val = np.max(data)
        if self.max_val == self.min_val:
            return np.zeros_like(data)
        return (data - self.min_val) / (self.max_val - self.min_val)
        
    def transform(self, data):
        if self.max_val == self.min_val:
            return np.zeros_like(data)
        return (data - self.min_val) / (self.max_val - self.min_val)
        
    def inverse_transform(self, scaled_data):
        return scaled_data * (self.max_val - self.min_val) + self.min_val

def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i:(i + seq_length)]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

def train_lstm_for_ticker(ticker: str, seq_length: int = 15, epochs: int = 30) -> str:
    """
    Downloads 3 years of data for the ticker, trains an LSTM model, and saves weights.
    Returns path to the saved model.
    """
    print(f"Training LSTM model for ticker {ticker}...")
    source = YFinanceSource()
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=3 * 365)).strftime("%Y-%m-%d")
    
    prices_data = source.get_history(ticker, start_date, end_date)
    if len(prices_data) < 50:
        raise ValueError(f"Insufficient historical data for {ticker} to train LSTM.")
        
    closes = np.array([p["close"] for p in prices_data], dtype=np.float32)
    
    # Scale data
    scaler = MinMaxScale()
    scaled_closes = scaler.fit_transform(closes)
    
    # Create sequences
    X, y = create_sequences(scaled_closes, seq_length)
    
    # Convert to PyTorch tensors
    X_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)  # [Batch, Seq, Features]
    y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)  # [Batch, Features]
    
    # Train
    model = LSTMForecaster(input_size=1, hidden_size=64, num_layers=2, output_size=1)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005)
    
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X_tensor)
        loss = criterion(outputs, y_tensor)
        loss.backward()
        optimizer.step()
        
    # Save model and scaling parameters
    model_path = os.path.join(MODELS_DIR, f"lstm_{ticker.upper()}.pt")
    torch.save({
        'model_state_dict': model.state_dict(),
        'min_val': float(scaler.min_val),
        'max_val': float(scaler.max_val),
        'seq_length': seq_length
    }, model_path)
    print(f"Model saved successfully to {model_path}")
    return model_path

def predict_future_trend(ticker: str, recent_prices: list, forecast_days: int = 30) -> dict:
    """
    Loads saved model, runs rolling 30-day forecast.
    recent_prices: list of floats representing last ~30 days of closes.
    Returns:
        {
            "forecast": list of floats,
            "expected_move": float percentage,
            "direction": str ("up" or "down" or "neutral")
        }
    """
    model_path = os.path.join(MODELS_DIR, f"lstm_{ticker.upper()}.pt")
    
    # Train if it doesn't exist
    if not os.path.exists(model_path):
        train_lstm_for_ticker(ticker)
        
    checkpoint = torch.load(model_path, map_location=torch.device('cpu'), weights_only=False)
    
    seq_length = checkpoint.get('seq_length', 15)
    min_val = checkpoint['min_val']
    max_val = checkpoint['max_val']
    
    scaler = MinMaxScale()
    scaler.min_val = min_val
    scaler.max_val = max_val
    
    # Load weights
    model = LSTMForecaster(input_size=1, hidden_size=64, num_layers=2, output_size=1)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    # Prepare input sequence of length seq_length
    input_seq = recent_prices[-seq_length:]
    if len(input_seq) < seq_length:
        # pad if too short
        input_seq = [recent_prices[0]] * (seq_length - len(input_seq)) + input_seq
        
    scaled_seq = scaler.transform(np.array(input_seq, dtype=np.float32))
    
    # Rolling forecast loop
    forecast = []
    current_seq = list(scaled_seq)
    
    with torch.no_grad():
        for _ in range(forecast_days):
            seq_tensor = torch.tensor([current_seq], dtype=torch.float32).unsqueeze(-1)  # [1, seq_length, 1]
            pred = model(seq_tensor).item()
            forecast.append(pred)
            
            # Slide window
            current_seq.pop(0)
            current_seq.append(pred)
            
    # Inverse scale predictions
    unscaled_forecast = scaler.inverse_transform(np.array(forecast, dtype=np.float32))
    unscaled_forecast = [round(float(val), 2) for val in unscaled_forecast]
    
    # Calculate percentage change
    start_price = recent_prices[-1]
    end_price = unscaled_forecast[-1]
    pct_change = ((end_price - start_price) / start_price) * 100
    
    direction = "neutral"
    if pct_change > 1.5:
        direction = "up"
    elif pct_change < -1.5:
        direction = "down"
        
    return {
        "forecast": unscaled_forecast,
        "expected_move": round(pct_change, 2),
        "direction": direction
    }
