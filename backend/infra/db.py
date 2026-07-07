from datetime import datetime
from typing import Any, Iterable

from sqlalchemy import (
    JSON,
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
)
from sqlalchemy.engine import Engine

from backend.infra.config import SETTINGS


metadata = MetaData()

etl_runs = Table(
    "etl_runs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("pipeline_name", String(120), nullable=False),
    Column("run_date", Date, nullable=False),
    Column("status", String(32), nullable=False),
    Column("records_pulled", Integer, nullable=False, default=0),
    Column("records_valid", Integer, nullable=False, default=0),
    Column("records_stored", Integer, nullable=False, default=0),
    Column("errors", JSON, nullable=True),
    Column("started_at", DateTime, nullable=False, default=datetime.utcnow),
    Column("finished_at", DateTime, nullable=True),
)

market_data = Table(
    "market_data",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("asset_class", String(40), nullable=False),
    Column("symbol", String(32), nullable=False),
    Column("as_of", Date, nullable=False),
    Column("open", Float, nullable=True),
    Column("high", Float, nullable=True),
    Column("low", Float, nullable=True),
    Column("close", Float, nullable=False),
    Column("volume", Float, nullable=True),
    Column("meta", JSON, nullable=True),
)

fundamental_data = Table(
    "fundamental_data",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("symbol", String(32), nullable=False),
    Column("as_of", Date, nullable=False),
    Column("revenue", Float, nullable=True),
    Column("eps", Float, nullable=True),
    Column("net_income", Float, nullable=True),
    Column("margins", Float, nullable=True),
    Column("cash_flow", Float, nullable=True),
    Column("debt", Float, nullable=True),
    Column("roe", Float, nullable=True),
    Column("roic", Float, nullable=True),
    Column("meta", JSON, nullable=True),
)

news_data = Table(
    "news_data",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("source_type", String(64), nullable=False),
    Column("source", String(120), nullable=False),
    Column("title", Text, nullable=False),
    Column("published_at", DateTime, nullable=True),
    Column("url", Text, nullable=True),
    Column("symbol", String(32), nullable=True),
    Column("summary", Text, nullable=True),
)

economic_data = Table(
    "economic_data",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("series_id", String(64), nullable=False),
    Column("series_name", String(180), nullable=False),
    Column("period_date", Date, nullable=False),
    Column("value", Float, nullable=False),
)


def get_engine() -> Engine:
    return create_engine(SETTINGS.postgres_url, future=True)


def init_infra_db() -> None:
    engine = get_engine()
    metadata.create_all(engine)


def insert_rows(table: Table, rows: Iterable[dict[str, Any]]) -> int:
    row_list = list(rows)
    if not row_list:
        return 0
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(table.insert(), row_list)
    return len(row_list)

