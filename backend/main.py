import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import torch

from backend.database import log_prediction, get_all_prediction_logs, cache_prices, get_cached_prices, update_prediction_outcome
from backend.data_sources import get_stock_source, calculate_technical_indicators
from backend.sentiment import get_sentiment_score
from backend.lstm_model import predict_future_trend, train_lstm_for_ticker
from backend.agent import generate_agent_reasoning
from backend.infra.pipeline import get_latest_runs, get_pipeline_status, run_nightly_etl
from backend.warehouse.db import init_warehouse_db, table_counts
from backend.warehouse.service import create_ai_report, seed_demo_warehouse
from backend.research.sec_filing_analyzer import analyze_sec_filing
from backend.research.earnings_call_analyzer import analyze_earnings_call
from backend.research.valuation_agent import ValuationInput, compute_valuation_metrics
from backend.research.rag_engine import index_documents, query_documents
from backend.copilot.engine import run_copilot

app = FastAPI(title="PreStocks AI Backend")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core stock specifications
STOCKS_METADATA = {
    "NVDA": {
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "category": "Semiconductors",
        "icon": "🤖",
        "desc": "NVIDIA Corporation focuses on personal computer graphics, graphics processing units, and also AI solutions. It is the leading provider of chips powering the global AI revolution.",
        "volatility": 0.28,
        "globalSensitivity": {
            "interestRates": -0.1,
            "tradeTensions": -0.6,
            "consumerSpending": 0.3
        }
    },
    "PLTR": {
        "symbol": "PLTR",
        "name": "Palantir Technologies Inc.",
        "category": "Software / AI",
        "icon": "🔮",
        "desc": "Palantir Technologies builds software platforms for big data analytics. Its platforms are heavily utilized by defense agencies and enterprise customers for operations.",
        "volatility": 0.32,
        "globalSensitivity": {
            "interestRates": -0.3,
            "tradeTensions": -0.2,
            "consumerSpending": 0.4
        }
    },
    "RKLB": {
        "symbol": "RKLB",
        "name": "Rocket Lab USA Inc.",
        "category": "Aerospace / Defense",
        "icon": "🚀",
        "desc": "Rocket Lab is an end-to-end space company. It delivers launch services, spacecraft manufacture, satellite components, and on-orbit management solutions.",
        "volatility": 0.40,
        "globalSensitivity": {
            "interestRates": -0.5,
            "tradeTensions": -0.3,
            "consumerSpending": 0.3
        }
    },
    "LUNR": {
        "symbol": "LUNR",
        "name": "Intuitive Machines Inc.",
        "category": "Aerospace / Space Exploration",
        "icon": "🌙",
        "desc": "Intuitive Machines is an American space exploration company focused on lunar landers, lunar surface operations, orbital services, and space communications.",
        "volatility": 0.55,
        "globalSensitivity": {
            "interestRates": -0.6,
            "tradeTensions": -0.2,
            "consumerSpending": 0.2
        }
    }
}

class PredictRequest(BaseModel):
    ticker: str
    macro_rates: int
    macro_trade: int
    macro_spending: int
    headline: str


class SecFilingAnalyzeRequest(BaseModel):
    filing_type: str
    filing_text: str
    symbol: str | None = None


class EarningsCallAnalyzeRequest(BaseModel):
    transcript: str
    symbol: str | None = None


class ValuationRequest(BaseModel):
    symbol: str
    price: float
    shares_outstanding: float
    free_cash_flow: float
    growth_rate: float
    discount_rate: float
    terminal_growth: float
    eps: float
    earnings_growth_rate: float
    ebitda: float
    enterprise_value: float
    revenue_growth: float
    profit_margin: float


class RagDocumentRequest(BaseModel):
    doc_type: str
    source: str | None = None
    symbol: str | None = None
    title: str
    content: str


class RagIndexRequest(BaseModel):
    documents: list[RagDocumentRequest]


class RagQueryRequest(BaseModel):
    question: str
    top_k: int = 5


class CopilotRequest(BaseModel):
    question: str
    risk_profile: str = "moderate"

@app.on_event("startup")
def on_startup():
    print("PreStocks backend starting up...")
    
    # 1. Warm up/Train LSTM models for core tickers if weights do not exist
    for ticker in STOCKS_METADATA.keys():
        model_path = os.path.join(os.path.dirname(__file__), "models", f"lstm_{ticker}.pt")
        if not os.path.exists(model_path):
            try:
                train_lstm_for_ticker(ticker, seq_length=15, epochs=30)
            except Exception as e:
                print(f"Could not pre-train {ticker}: {e}")
                
    # 2. Check pending predictions and audit them using historical prices
    try:
        check_prediction_outcomes()
    except Exception as e:
        print(f"Error auditing predictions: {e}")

    # 3. Initialize data infra tables and status cache by reading pipeline status.
    try:
        get_pipeline_status()
    except Exception as e:
        print(f"Infra initialization warning: {e}")

def check_prediction_outcomes():
    """
    Check if target dates of pending predictions have arrived,
    download actual prices, and update database outcomes.
    """
    from backend.database import get_pending_predictions
    pending = get_pending_predictions()
    if not pending:
        return
        
    print(f"Found {len(pending)} pending predictions to verify.")
    source = get_stock_source()
    
    for pred in pending:
        ticker = pred["ticker"]
        target_date_str = pred["target_date"]
        pred_id = pred["id"]
        
        # Download price for that date (we fetch 3 days around target to cover weekends/holidays)
        target_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
        start_date = (target_dt - timedelta(days=2)).strftime("%Y-%m-%d")
        end_date = (target_dt + timedelta(days=2)).strftime("%Y-%m-%d")
        
        history = source.get_history(ticker, start_date, end_date)
        if not history:
            continue
            
        # Find closest trading day close
        actual_close = history[-1]["close"]  # Fallback to last available
        for p in history:
            if p["date"] >= target_date_str:
                actual_close = p["close"]
                break
                
        # Calculate moves
        # We need the base price (price at the time prediction was made)
        # We estimate base price by: target_price / (1 + predicted_move/100)
        predicted_move = pred["predicted_move"]
        target_price = pred["target_price"]
        
        base_price = target_price / (1 + predicted_move / 100.0) if predicted_move != -100 else target_price
        actual_move = ((actual_close - base_price) / base_price) * 100.0 if base_price > 0 else 0.0
        
        # Was the direction prediction correct?
        is_correct = 0
        if predicted_move > 0 and actual_move > 0:
            is_correct = 1
        elif predicted_move < 0 and actual_move < 0:
            is_correct = 1
        elif predicted_move == 0 and actual_move == 0:
            is_correct = 1
            
        update_prediction_outcome(pred_id, round(actual_close, 2), is_correct)
        print(f"Updated prediction ID {pred_id} ({ticker}): Pred move {predicted_move:.1f}%, Actual move {actual_move:.1f}%, Correct={is_correct}")

@app.get("/stocks")
def get_stocks():
    """
    Returns current quotes and metadata for our core 4 tickers.
    """
    source = get_stock_source()
    results = {}
    for symbol, meta in STOCKS_METADATA.items():
        quote = source.get_live_quote(symbol)
        results[symbol] = {
            **meta,
            "price": quote["price"],
            "change": quote["change"],
            "change_pct": quote["change_pct"]
        }
    return results

@app.post("/predict")
def predict_market(req: PredictRequest):
    ticker = req.ticker.upper()
    if ticker not in STOCKS_METADATA:
        raise HTTPException(status_code=400, detail=f"Unsupported ticker: {ticker}")
        
    source = get_stock_source()
    
    # 1. Fetch History (Recent 45 days to compute technicals + LSTM seq length)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    
    # Check cache first
    history = get_cached_prices(ticker, start_date, end_date)
    if not history:
        history = source.get_history(ticker, start_date, end_date)
        if history:
            cache_prices(ticker, history)
            
    if not history:
        raise HTTPException(status_code=500, detail=f"Failed to load historical prices for {ticker}")
        
    # Get recent closes
    closes = [p["close"] for p in history]
    current_price = closes[-1]
    
    # 2. Compute Technical Indicators
    technicals = calculate_technical_indicators(history)
    
    # 3. FinBERT news sentiment scoring
    sentiment = get_sentiment_score(req.headline)
    
    # 4. LSTM price forecasting
    lstm_out = predict_future_trend(ticker, closes, forecast_days=30)
    
    # 5. Agentic synthesis (Claude API / Fallback rules)
    agent_decision = generate_agent_reasoning(
        ticker=ticker,
        macro_rates=req.macro_rates,
        macro_trade=req.macro_trade,
        macro_spending=req.macro_spending,
        headline=req.headline,
        lstm_result=lstm_out,
        sentiment_result=sentiment,
        technical_result=technicals
    )
    
    # 6. Log prediction to DB
    # Target date is 30 days from now
    target_dt = datetime.now() + timedelta(days=30)
    target_date_str = target_dt.strftime("%Y-%m-%d")
    
    # Estimated target price based on agent predicted move
    predicted_pct = agent_decision["predicted_move"]
    target_price = current_price * (1 + predicted_pct / 100.0)
    
    log_prediction(
        ticker=ticker,
        macro_rates=req.macro_rates,
        macro_trade=req.macro_trade,
        macro_spending=req.macro_spending,
        headline=req.headline,
        lstm_predicted_trend=lstm_out["expected_move"],
        sentiment_score=sentiment["score"],
        agent_decision=agent_decision["decision"],
        agent_reasoning=agent_decision["reasoning"],
        predicted_move=predicted_pct,
        target_date=target_date_str,
        target_price=round(target_price, 2)
    )
    
    # Prepare 1M chart arrays
    # History (last 30 days)
    chart_history = history[-30:]
    
    # Projected prices forecast paths mapping
    forecast_path = []
    temp_price = current_price
    drift = (predicted_pct / 100.0) / 30.0
    
    for i in range(1, 31):
        temp_price = temp_price * (1 + drift)
        forecast_dt = datetime.now() + timedelta(days=i)
        forecast_path.append({
            "price": round(temp_price, 2),
            "label": f"Day +{i}"
        })
        
    return {
        "ticker": ticker,
        "sentimentScore": int(50 + (sentiment["score"] / 2.0)),  # Rescale -100..100 to 0..100
        "isBullish": predicted_pct >= 0,
        "expectedMove": round(predicted_pct, 2),
        "explanation": agent_decision["reasoning"],
        "history": chart_history,
        "forecast": forecast_path,
        "sentiment_raw": sentiment,
        "lstm_raw": lstm_out,
        "technical_raw": technicals
    }

@app.get("/logs")
def get_logs():
    return get_all_prediction_logs()


@app.get("/infra/status")
def get_infra_status():
    """
    Returns health/status overview for Phase 1 ETL pipelines.
    """
    return get_pipeline_status()


@app.get("/infra/runs")
def get_infra_runs(limit: int = 25):
    """
    Returns latest ETL runs for monitoring website view.
    """
    return get_latest_runs(limit=limit)


@app.post("/infra/run-nightly")
def trigger_nightly_infra_pipeline():
    """
    Manually trigger nightly ETL pipeline sequence.
    """
    try:
        results = run_nightly_etl()
        return {
            "status": "ok",
            "runs": [
                {
                    "pipeline_name": r.pipeline_name,
                    "status": r.status,
                    "records_pulled": r.records_pulled,
                    "records_valid": r.records_valid,
                    "records_stored": r.records_stored,
                    "errors": r.errors,
                }
                for r in results
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Nightly ETL trigger failed: {exc}") from exc


@app.post("/warehouse/init")
def warehouse_init():
    init_warehouse_db()
    return {"status": "ok", "tables": table_counts()}


@app.post("/warehouse/seed-demo")
def warehouse_seed_demo():
    counts = seed_demo_warehouse()
    return {"status": "ok", "tables": counts}


@app.get("/warehouse/status")
def warehouse_status():
    init_warehouse_db()
    return {"status": "ok", "tables": table_counts()}


@app.post("/ai/sec-filing/analyze")
def ai_sec_filing_analyze(req: SecFilingAnalyzeRequest):
    result = analyze_sec_filing(req.filing_type, req.filing_text)
    report_id = create_ai_report(
        report_type="sec_filing_analysis",
        title=f"{req.symbol or 'UNKNOWN'} {req.filing_type} analysis",
        content=result.get("management_commentary", ["No commentary extracted."])[0]
        if result.get("management_commentary")
        else "No commentary extracted.",
        metadata_json=result,
    )
    return {"report_id": report_id, "analysis": result}


@app.post("/ai/earnings-call/analyze")
def ai_earnings_call_analyze(req: EarningsCallAnalyzeRequest):
    result = analyze_earnings_call(req.transcript)
    report_id = create_ai_report(
        report_type="earnings_call_analysis",
        title=f"{req.symbol or 'UNKNOWN'} earnings call analysis",
        content=result.get("sentiment", {}).get("label", "neutral"),
        metadata_json=result,
    )
    return {"report_id": report_id, "analysis": result}


@app.post("/ai/valuation")
def ai_valuation(req: ValuationRequest):
    val_input = ValuationInput(**req.dict())
    result = compute_valuation_metrics(val_input)
    report_id = create_ai_report(
        report_type="valuation_analysis",
        title=f"{req.symbol} valuation analysis",
        content=result.get("explanation", ""),
        metadata_json=result,
    )
    return {"report_id": report_id, "valuation": result}


@app.post("/rag/index")
def rag_index(req: RagIndexRequest):
    payload = [doc.dict() for doc in req.documents]
    result = index_documents(payload)
    return {"status": "ok", **result}


@app.post("/rag/query")
def rag_query(req: RagQueryRequest):
    return query_documents(req.question, top_k=req.top_k)


@app.post("/copilot/query")
def copilot_query(req: CopilotRequest):
    result = run_copilot(req.question, risk_profile=req.risk_profile)
    report_id = create_ai_report(
        report_type="copilot_response",
        title="Investment Copilot response",
        content=result.get("answer", ""),
        metadata_json=result,
    )
    return {"report_id": report_id, "result": result}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
