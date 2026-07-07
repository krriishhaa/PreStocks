"""
Seed script — populates learning modules on first boot.
Idempotent: skips if modules already exist.
"""
import sys
sys.path.insert(0, ".")

from app.database.session import SessionLocal
from app.models.learning import LearningModule

MODULES = [
    {"slug": "stocks-101", "title": "Stocks 101", "description": "What is a stock, why do prices move", "tier": "beginner", "duration_minutes": 8, "order_index": 1},
    {"slug": "pe-ratios", "title": "Understanding P/E Ratios", "description": "Valuation basics and how to interpret them", "tier": "beginner", "duration_minutes": 6, "order_index": 2},
    {"slug": "risk-reward", "title": "Risk vs. Reward", "description": "How to think about risk in investing", "tier": "beginner", "duration_minutes": 7, "order_index": 3},
    {"slug": "financial-statements", "title": "Reading Financial Statements", "description": "Balance sheet, income statement, cash flow basics", "tier": "beginner", "duration_minutes": 10, "order_index": 4},
    {"slug": "diversification", "title": "Diversification", "description": "Why and how to diversify your portfolio", "tier": "beginner", "duration_minutes": 6, "order_index": 5},
    {"slug": "technical-analysis", "title": "Technical Analysis Intro", "description": "Charts, trends, moving averages, and indicators", "tier": "intermediate", "duration_minutes": 12, "order_index": 6},
    {"slug": "earnings-volatility", "title": "Earnings & Volatility", "description": "What happens around earnings reports", "tier": "intermediate", "duration_minutes": 9, "order_index": 7},
    {"slug": "options-basics", "title": "Options Basics", "description": "Calls, puts, and why they matter for stock investors", "tier": "intermediate", "duration_minutes": 15, "order_index": 8},
    {"slug": "sector-rotation", "title": "Sector Rotation", "description": "How money flows between sectors in different market cycles", "tier": "intermediate", "duration_minutes": 10, "order_index": 9},
    {"slug": "portfolio-theory", "title": "Modern Portfolio Theory", "description": "Efficient frontier and optimal asset allocation", "tier": "advanced", "duration_minutes": 14, "order_index": 10},
    {"slug": "algorithmic-strategies", "title": "Algorithmic Trading Concepts", "description": "How quant strategies work at a high level", "tier": "advanced", "duration_minutes": 12, "order_index": 11},
    {"slug": "macro-indicators", "title": "Macro Economic Indicators", "description": "Fed rates, CPI, GDP and their market impact", "tier": "advanced", "duration_minutes": 11, "order_index": 12},
]


def seed():
    db = SessionLocal()
    try:
        existing = db.query(LearningModule).count()
        if existing > 0:
            print(f"Seed skipped — {existing} modules already exist.")
            return

        for m in MODULES:
            db.add(LearningModule(**m))

        db.commit()
        print(f"Seeded {len(MODULES)} learning modules.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
