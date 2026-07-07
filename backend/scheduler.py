import os
from datetime import datetime, timedelta
import json

from backend.database import get_db_connection, get_pending_predictions
from backend.data_sources import get_stock_source, calculate_technical_indicators
from backend.sentiment import get_sentiment_score
from backend.lstm_model import predict_future_trend
from backend.agent import generate_agent_reasoning
from backend.main import check_prediction_outcomes

REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "the_kri_report.md")

def run_daily_scheduler():
    print("Running scheduled daily agent report...")
    
    # 1. Audit older predictions
    try:
        check_prediction_outcomes()
    except Exception as e:
        print(f"Error auditing outcomes: {e}")
        
    # 2. Generate new signals for NVDA, PLTR, RKLB, LUNR
    tickers = ["NVDA", "PLTR", "RKLB", "LUNR"]
    source = get_stock_source()
    
    signals = []
    
    for ticker in tickers:
        try:
            print(f"Processing signal for {ticker}...")
            # Get live quote
            quote = source.get_live_quote(ticker)
            
            # Fetch recent 45 days prices
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
            history = source.get_history(ticker, start_date, end_date)
            closes = [p["close"] for p in history]
            
            # Get latest news
            news = source.get_recent_news(ticker)
            headline = news[0]["headline"] if news else "No new press releases detected. Broad sector trend dominates."
            
            # Run signals
            sentiment = get_sentiment_score(headline)
            technicals = calculate_technical_indicators(history)
            lstm_out = predict_future_trend(ticker, closes, forecast_days=30)
            
            # Agent reasoning (assume medium/stable baseline macro parameters)
            agent_decision = generate_agent_reasoning(
                ticker=ticker,
                macro_rates=1,  # Medium
                macro_trade=1,  # Moderate
                macro_spending=1,  # Stable
                headline=headline,
                lstm_result=lstm_out,
                sentiment_result=sentiment,
                technical_result=technicals
            )
            
            signals.append({
                "ticker": ticker,
                "price": quote["price"],
                "change_pct": quote["change_pct"],
                "decision": agent_decision["decision"],
                "reasoning": agent_decision["reasoning"],
                "predicted_move": agent_decision["predicted_move"],
                "headline": headline,
                "sentiment_lbl": sentiment["label"],
                "tech_signal": technicals["signal"],
                "lstm_move": lstm_out["expected_move"]
            })
        except Exception as e:
            print(f"Error generating signal for {ticker}: {e}")
            
    # 3. Compile the Markdown report ("The Kri Report")
    report_md = f"""# 🏹 The Kri Report - AI Market Signals & Reasoning
Generated: {datetime.now().strftime("%B %d, %Y %I:%M %p")}

Welcome to your daily continuous prediction report. Our agentic reasoning system (Claude API + PyTorch LSTM + FinBERT news sentiment) has synthesized multi-modal data streams for our core tickers.

---

## 📊 Summary of Daily Signals

| Ticker | Price | Daily Chg | Decision | Projected 30D Move | Tech Signal | News Sentiment |
|--------|-------|-----------|----------|--------------------|-------------|----------------|
"""
    
    for sig in signals:
        badge = "🟢 BUY" if sig["decision"] == "BUY" else "🔴 SELL" if sig["decision"] == "SELL" else "🟡 HOLD" if sig["decision"] == "HOLD" else "🔍 WATCH" if sig["decision"] == "WATCH" else "⚠️ AVOID"
        
        move_sign = "+" if sig["predicted_move"] >= 0 else ""
        report_md += f"| **{sig['ticker']}** | ${sig['price']:.2f} | {sig['change_pct']:+.2f}% | {badge} | {move_sign}{sig['predicted_move']:.1f}% | {sig['tech_signal']} | {sig['sentiment_lbl']} |\n"
        
    report_md += "\n---\n\n## 🔮 Detail Agent Analysis & Conflict Resolutions\n\n"
    
    for sig in signals:
        report_md += f"### {sig['ticker']} (${sig['price']:.2f})\n"
        report_md += f"- **Latest Headline Event**: *\"{sig['headline']}\"*\n"
        report_md += f"- **LSTM Trend Forecast**: {sig['lstm_move']:+.1f}% over 30 days\n"
        report_md += f"- **Technicals Context**: {sig['tech_signal']}\n"
        report_md += f"- **Agent Decision reasoning**: {sig['reasoning']}\n\n"
        
    report_md += """
---
*Disclaimer: PreStocks is a virtual learning and simulation platform. None of the signals or statements in this report constitute actual financial or investment advice. Always perform your own research before committing real capital.*
"""
    
    # Write report
    with open(REPORT_PATH, "w") as f:
        f.write(report_md)
        
    print(f"Daily signal newsletter compiled and saved to {os.path.abspath(REPORT_PATH)}")
    print("Email transmission simulated successfully.")

if __name__ == "__main__":
    run_daily_scheduler()
