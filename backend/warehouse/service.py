from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import select

from backend.warehouse.db import (
    ai_reports,
    companies,
    earnings_calls,
    financials,
    get_engine,
    init_warehouse_db,
    insert_rows,
    news,
    portfolios,
    prices,
    table_counts,
    transactions,
    users,
    watchlists,
)


def ensure_company(symbol: str, name: str, sector: str | None = None) -> int:
    init_warehouse_db()
    engine = get_engine()
    with engine.begin() as conn:
        existing = conn.execute(select(companies).where(companies.c.symbol == symbol.upper())).mappings().first()
        if existing:
            return int(existing["id"])
        result = conn.execute(
            companies.insert().values(
                symbol=symbol.upper(),
                name=name,
                sector=sector,
                is_active=True,
            )
        )
        return int(result.inserted_primary_key[0])


def create_ai_report(
    report_type: str,
    title: str,
    content: str,
    metadata_json: dict[str, Any] | None = None,
    user_id: int | None = None,
    company_id: int | None = None,
) -> int:
    init_warehouse_db()
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(
            ai_reports.insert().values(
                report_type=report_type,
                title=title,
                content=content,
                metadata_json=metadata_json or {},
                user_id=user_id,
                company_id=company_id,
            )
        )
        return int(result.inserted_primary_key[0])


def seed_demo_warehouse() -> dict[str, int]:
    init_warehouse_db()
    nvda_id = ensure_company("NVDA", "NVIDIA Corporation", "Semiconductors")
    msft_id = ensure_company("MSFT", "Microsoft Corporation", "Software")

    insert_rows(
        users,
        [
            {
                "email": "demo@prestocks.local",
                "full_name": "Demo User",
                "risk_profile": "moderate",
                "tax_bracket": 0.24,
                "created_at": datetime.utcnow(),
            }
        ],
    )

    insert_rows(
        prices,
        [
            {
                "company_id": nvda_id,
                "as_of": date.today(),
                "open": 145.1,
                "high": 149.8,
                "low": 143.5,
                "close": 148.9,
                "volume": 23_450_000,
                "source": "seed",
            },
            {
                "company_id": msft_id,
                "as_of": date.today(),
                "open": 435.0,
                "high": 440.2,
                "low": 431.7,
                "close": 438.4,
                "volume": 12_280_000,
                "source": "seed",
            },
        ],
    )

    insert_rows(
        financials,
        [
            {
                "company_id": nvda_id,
                "period_end": date(2026, 3, 31),
                "period_type": "quarterly",
                "revenue": 26500.0,
                "eps": 2.12,
                "net_income": 14500.0,
                "margins": 0.42,
                "cash_flow": 9600.0,
                "debt": 9800.0,
                "roe": 0.52,
                "roic": 0.38,
                "raw_payload": {"source": "seed"},
            }
        ],
    )

    insert_rows(
        news,
        [
            {
                "company_id": nvda_id,
                "source": "Reuters",
                "title": "NVIDIA expands AI datacenter partnerships",
                "url": "https://example.com/nvda-news",
                "published_at": datetime.utcnow(),
                "summary": "Major hyperscaler expansion announced.",
                "sentiment_score": 0.73,
            }
        ],
    )

    insert_rows(
        earnings_calls,
        [
            {
                "company_id": nvda_id,
                "fiscal_period": "Q1-2026",
                "call_date": date.today(),
                "transcript": "We see strong demand, expanding margins, and robust enterprise adoption.",
                "analysis": {},
            }
        ],
    )

    # Lightweight placeholders for remaining warehouse tables.
    insert_rows(watchlists, [])
    insert_rows(portfolios, [])
    insert_rows(transactions, [])

    return table_counts()

