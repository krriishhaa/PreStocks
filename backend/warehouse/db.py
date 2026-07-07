from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    func,
    select,
)
from sqlalchemy.engine import Engine


WAREHOUSE_DB_URL = os.getenv("WAREHOUSE_DB_URL", "sqlite:///backend/prestocks_warehouse.db")
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("email", String(255), nullable=False, unique=True),
    Column("full_name", String(255), nullable=True),
    Column("risk_profile", String(32), nullable=True),
    Column("tax_bracket", Float, nullable=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)

companies = Table(
    "companies",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("symbol", String(32), nullable=False, unique=True),
    Column("name", String(255), nullable=False),
    Column("sector", String(120), nullable=True),
    Column("industry", String(120), nullable=True),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)

prices = Table(
    "prices",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("company_id", Integer, ForeignKey("companies.id"), nullable=False),
    Column("as_of", Date, nullable=False),
    Column("open", Float, nullable=True),
    Column("high", Float, nullable=True),
    Column("low", Float, nullable=True),
    Column("close", Float, nullable=False),
    Column("volume", Float, nullable=True),
    Column("source", String(64), nullable=True),
)

financials = Table(
    "financials",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("company_id", Integer, ForeignKey("companies.id"), nullable=False),
    Column("period_end", Date, nullable=False),
    Column("period_type", String(16), nullable=False, default="quarterly"),
    Column("revenue", Float, nullable=True),
    Column("eps", Float, nullable=True),
    Column("net_income", Float, nullable=True),
    Column("margins", Float, nullable=True),
    Column("cash_flow", Float, nullable=True),
    Column("debt", Float, nullable=True),
    Column("roe", Float, nullable=True),
    Column("roic", Float, nullable=True),
    Column("raw_payload", JSON, nullable=True),
)

news = Table(
    "news",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("company_id", Integer, ForeignKey("companies.id"), nullable=True),
    Column("source", String(120), nullable=False),
    Column("title", Text, nullable=False),
    Column("url", Text, nullable=True),
    Column("published_at", DateTime, nullable=True),
    Column("summary", Text, nullable=True),
    Column("sentiment_score", Float, nullable=True),
)

earnings_calls = Table(
    "earnings_calls",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("company_id", Integer, ForeignKey("companies.id"), nullable=False),
    Column("fiscal_period", String(32), nullable=False),
    Column("call_date", Date, nullable=True),
    Column("transcript", Text, nullable=False),
    Column("analysis", JSON, nullable=True),
)

watchlists = Table(
    "watchlists",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("name", String(120), nullable=False, default="Default"),
    Column("symbols", JSON, nullable=False, default=list),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)

portfolios = Table(
    "portfolios",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("name", String(120), nullable=False),
    Column("cash_balance", Float, nullable=False, default=0.0),
    Column("holdings", JSON, nullable=False, default=dict),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)

transactions = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("portfolio_id", Integer, ForeignKey("portfolios.id"), nullable=False),
    Column("company_id", Integer, ForeignKey("companies.id"), nullable=True),
    Column("txn_type", String(16), nullable=False),
    Column("quantity", Float, nullable=False),
    Column("price", Float, nullable=False),
    Column("fees", Float, nullable=False, default=0.0),
    Column("executed_at", DateTime, nullable=False, default=datetime.utcnow),
    Column("notes", Text, nullable=True),
)

ai_reports = Table(
    "ai_reports",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=True),
    Column("company_id", Integer, ForeignKey("companies.id"), nullable=True),
    Column("report_type", String(64), nullable=False),
    Column("title", String(255), nullable=False),
    Column("content", Text, nullable=False),
    Column("metadata_json", JSON, nullable=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)

rag_documents = Table(
    "rag_documents",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("doc_type", String(64), nullable=False),
    Column("source", String(120), nullable=True),
    Column("symbol", String(32), nullable=True),
    Column("title", String(255), nullable=False),
    Column("content", Text, nullable=False),
    Column("embedding", JSON, nullable=False),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)


def get_engine() -> Engine:
    return create_engine(WAREHOUSE_DB_URL, future=True)


def init_warehouse_db() -> None:
    engine = get_engine()
    metadata.create_all(engine)


def table_counts() -> dict[str, int]:
    init_warehouse_db()
    engine = get_engine()
    out: dict[str, int] = {}
    with engine.begin() as conn:
        for name, table in metadata.tables.items():
            out[name] = conn.execute(select(func.count()).select_from(table)).scalar_one()
    return out


def insert_rows(table: Table, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(table.insert(), rows)
    return len(rows)

