import os
import sys

# Ensure backend is in the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.database import init_db, log_prediction, get_all_prediction_logs, get_recent_failures
from backend.data_sources import get_stock_source, calculate_technical_indicators
from backend.sentiment import get_sentiment_score
from backend.lstm_model import train_lstm_for_ticker, predict_future_trend

def test_pipeline():
    print("=== STARTING BACKEND PIPELINE TESTS ===")
    
    # 1. Test Database
    print("\n1. Testing SQLite Database...")
    init_db()
    db_path = os.path.join(os.path.dirname(__file__), "prestocks.db")
    print(f"Database exists: {os.path.exists(db_path)}")
    
    # 2. Test Data Sources
    print("\n2. Testing Yahoo Finance Data Fetching...")
    source = get_stock_source()
    quote = source.get_live_quote("PLTR")
    print(f"PLTR Live Quote: {quote}")
    
    history = source.get_history("PLTR", "2026-05-01", "2026-06-01")
    print(f"PLTR History fetched: {len(history)} trading days.")
    assert len(history) > 0, "History fetch failed"
    
    techs = calculate_technical_indicators(history)
    print(f"PLTR Technical Indicators (May 2026): RSI={techs['rsi']}, Signal={techs['signal']}")
    
    # 3. Test News Sentiment (FinBERT / Fallback)
    print("\n3. Testing Sentiment Analysis...")
    text_bullish = "NVDA announces new breakthrough in quantum computing, stock surges"
    text_bearish = "Global semiconductor tariffs disrupt hardware supply chain"
    
    sent_bull = get_sentiment_score(text_bullish)
    sent_bear = get_sentiment_score(text_bearish)
    
    print(f"Bullish Text Score: {sent_bull['score']} ({sent_bull['label']}) [Source: {sent_bull['source']}]")
    print(f"Bearish Text Score: {sent_bear['score']} ({sent_bear['label']}) [Source: {sent_bear['source']}]")
    
    # 4. Test LSTM Training and Prediction
    print("\n4. Testing LSTM Training & Prediction...")
    # Train LUNR (smaller model/fewer epochs for testing)
    model_path = train_lstm_for_ticker("LUNR", seq_length=10, epochs=15)
    print(f"LSTM model trained and saved to: {model_path}")
    
    closes = [p["close"] for p in history]
    forecast = predict_future_trend("LUNR", closes, forecast_days=10)
    print(f"LUNR 10-day forecast: {forecast['forecast'][:5]}... Expected move: {forecast['expected_move']}%")
    
    # 5. Test Agent Reasoning
    from backend.agent import generate_agent_reasoning
    print("\n5. Testing Agent Reasoning Synthesis...")
    agent_out = generate_agent_reasoning(
        ticker="PLTR",
        macro_rates=2,  # Restrictive
        macro_trade=2,  # Tariffs high
        macro_spending=0,  # Recessionary
        headline="Palantir wins massive military AI contract, stock surges",
        lstm_result=forecast,
        sentiment_result=sent_bull,
        technical_result=techs
    )
    print(f"Agent Decision: {agent_out['decision']}")
    print(f"Agent Reasoning: {agent_out['reasoning']}")
    print(f"Agent Predicted Move: {agent_out['predicted_move']}%")
    
    # 6. Test Logging to DB
    print("\n6. Testing Database Logging...")
    pred_id = log_prediction(
        ticker="PLTR",
        macro_rates=2,
        macro_trade=2,
        macro_spending=0,
        headline="Palantir contract",
        lstm_predicted_trend=forecast["expected_move"],
        sentiment_score=sent_bull["score"],
        agent_decision=agent_out["decision"],
        agent_reasoning=agent_out["reasoning"],
        predicted_move=agent_out["predicted_move"],
        target_date="2026-07-25",
        target_price=26.50
    )
    print(f"Prediction logged with ID: {pred_id}")
    
    logs = get_all_prediction_logs()
    print(f"Total prediction logs in DB: {len(logs)}")
    
    print("\n=== ALL TESTS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_pipeline()
