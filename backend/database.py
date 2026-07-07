import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "prestocks.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Price cache table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_cache (
        ticker TEXT,
        date TEXT,
        close REAL,
        PRIMARY KEY (ticker, date)
    )
    """)
    
    # 2. Predictions logger table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        timestamp TEXT,
        macro_rates INTEGER,
        macro_trade INTEGER,
        macro_spending INTEGER,
        headline TEXT,
        lstm_predicted_trend REAL,
        sentiment_score REAL,
        agent_decision TEXT,
        agent_reasoning TEXT,
        predicted_move REAL,
        target_date TEXT,
        target_price REAL,
        actual_close REAL,
        is_correct INTEGER,
        outcome_checked INTEGER DEFAULT 0
    )
    """)
    
    conn.commit()
    conn.close()

def cache_prices(ticker: str, prices: list):
    """
    prices: list of dicts like [{"date": "2026-06-25", "close": 175.50}, ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    for p in prices:
        cursor.execute("""
        INSERT OR REPLACE INTO price_cache (ticker, date, close)
        VALUES (?, ?, ?)
        """, (ticker.upper(), p["date"], p["close"]))
    conn.commit()
    conn.close()

def get_cached_prices(ticker: str, start_date: str, end_date: str) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT date, close FROM price_cache
    WHERE ticker = ? AND date >= ? AND date <= ?
    ORDER BY date ASC
    """, (ticker.upper(), start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return [{"date": row["date"], "close": row["close"]} for row in rows]

def log_prediction(ticker: str, macro_rates: int, macro_trade: int, macro_spending: int, 
                   headline: str, lstm_predicted_trend: float, sentiment_score: float, 
                   agent_decision: str, agent_reasoning: str, predicted_move: float, 
                   target_date: str, target_price: float) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    cursor.execute("""
    INSERT INTO predictions (
        ticker, timestamp, macro_rates, macro_trade, macro_spending,
        headline, lstm_predicted_trend, sentiment_score, agent_decision,
        agent_reasoning, predicted_move, target_date, target_price
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticker.upper(), timestamp, macro_rates, macro_trade, macro_spending,
          headline, lstm_predicted_trend, sentiment_score, agent_decision,
          agent_reasoning, predicted_move, target_date, target_price))
    pred_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return pred_id

def get_pending_predictions() -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    # Find predictions where target_date has passed or is today, but outcome has not been checked
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    cursor.execute("""
    SELECT * FROM predictions
    WHERE outcome_checked = 0 AND target_date <= ?
    """, (today_str,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_prediction_outcome(pred_id: int, actual_close: float, is_correct: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE predictions
    SET actual_close = ?, is_correct = ?, outcome_checked = 1
    WHERE id = ?
    """, (actual_close, is_correct, pred_id))
    conn.commit()
    conn.close()

def get_recent_failures(limit: int = 5) -> list:
    """
    Returns the most recent predictions that were wrong to serve as few-shot negative examples for the LLM.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT ticker, headline, agent_decision, agent_reasoning, predicted_move, actual_close, target_price
    FROM predictions
    WHERE outcome_checked = 1 AND is_correct = 0
    ORDER BY timestamp DESC
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_prediction_logs() -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM predictions
    ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Auto-initialize database when this module is imported
init_db()
