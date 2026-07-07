"""Initial schema - all tables

Revision ID: 001_initial
Revises:
Create Date: 2026-07-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("age", sa.Integer()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("risk_tier", sa.String(50)),
    )
    op.create_index("idx_user_email", "user", ["email"])

    # User Risk Profiles
    op.create_table(
        "user_risk_profile",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE")),
        sa.Column("risk_tolerance_score", sa.Integer()),
        sa.Column("knowledge_level", sa.Integer()),
        sa.Column("assessment_date", sa.DateTime(), server_default=sa.func.now()),
    )

    # Stocks
    op.create_table(
        "stock",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("ticker", sa.String(10), unique=True, nullable=False),
        sa.Column("company_name", sa.String(255)),
        sa.Column("sector", sa.String(100)),
        sa.Column("industry", sa.String(100)),
        sa.Column("market_cap", sa.BigInteger()),
        sa.Column("last_updated", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("idx_stock_ticker", "stock", ["ticker"])

    # Stock Fundamentals
    op.create_table(
        "stock_fundamentals",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("stock_id", sa.Integer(), sa.ForeignKey("stock.id")),
        sa.Column("quarter_date", sa.Date()),
        sa.Column("pe_ratio", sa.Float()),
        sa.Column("price_to_sales", sa.Float()),
        sa.Column("debt_to_equity", sa.Float()),
        sa.Column("current_ratio", sa.Float()),
        sa.Column("interest_coverage", sa.Float()),
        sa.Column("cash_runway_months", sa.Integer()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("stock_id", "quarter_date", name="uq_fundamentals_stock_quarter"),
    )

    # Stock Prices (TimescaleDB hypertable)
    op.create_table(
        "stock_prices",
        sa.Column("time", sa.DateTime(), nullable=False),
        sa.Column("stock_id", sa.Integer(), sa.ForeignKey("stock.id"), nullable=False),
        sa.Column("open", sa.Float()),
        sa.Column("high", sa.Float()),
        sa.Column("low", sa.Float()),
        sa.Column("close", sa.Float()),
        sa.Column("volume", sa.BigInteger()),
    )
    op.create_index("idx_stock_prices_stock_time", "stock_prices", ["stock_id", sa.text("time DESC")])
    # Note: Run manually after migration:
    # SELECT create_hypertable('stock_prices', 'time', if_not_exists => TRUE);

    # Risk Flags
    op.create_table(
        "risk_flag",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("stock_id", sa.Integer(), sa.ForeignKey("stock.id")),
        sa.Column("flag_type", sa.String(50)),
        sa.Column("severity_score", sa.Integer()),
        sa.Column("explanation", sa.Text()),
        sa.Column("confidence_score", sa.Float()),
        sa.Column("calculated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("stock_id", "flag_type", "calculated_at", name="uq_risk_flag_stock_type_time"),
    )
    op.create_index("idx_risk_flag_stock", "risk_flag", ["stock_id", sa.text("calculated_at DESC")])

    # Portfolios
    op.create_table(
        "portfolio",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("total_value", sa.Float(), server_default="10000.00"),
        sa.Column("cash_available", sa.Float(), server_default="10000.00"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", name="uq_portfolio_user"),
    )

    # Holdings
    op.create_table(
        "holding",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("portfolio_id", sa.Integer(), sa.ForeignKey("portfolio.id", ondelete="CASCADE")),
        sa.Column("stock_id", sa.Integer(), sa.ForeignKey("stock.id")),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("average_buy_price", sa.Float(), nullable=False),
        sa.Column("acquired_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("idx_holding_portfolio", "holding", ["portfolio_id"])

    # Trades
    op.create_table(
        "trade",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("portfolio_id", sa.Integer(), sa.ForeignKey("portfolio.id")),
        sa.Column("stock_id", sa.Integer(), sa.ForeignKey("stock.id")),
        sa.Column("order_type", sa.String(10)),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("price_executed", sa.Float(), nullable=False),
        sa.Column("total_value", sa.Float(), nullable=False),
        sa.Column("executed_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("order_ticket_details", JSONB()),
    )
    op.create_index("idx_trade_portfolio", "trade", ["portfolio_id", sa.text("executed_at DESC")])

    # Learning Modules
    op.create_table(
        "learning_module",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("title", sa.String(255)),
        sa.Column("description", sa.Text()),
        sa.Column("required_tier", sa.String(50)),
        sa.Column("content_url", sa.Text()),
        sa.Column("estimated_duration_minutes", sa.Integer()),
        sa.Column("quiz_questions", JSONB()),
        sa.Column("created_at", sa.DateTime()),
    )

    # User Module Progress
    op.create_table(
        "user_module_progress",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE")),
        sa.Column("module_id", sa.Integer(), sa.ForeignKey("learning_module.id")),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("quiz_score", sa.Integer()),
        sa.UniqueConstraint("user_id", "module_id", name="uq_user_module_progress"),
    )

    # Social Posts
    op.create_table(
        "social_post",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE")),
        sa.Column("content", sa.Text()),
        sa.Column("tickers", ARRAY(sa.String())),
        sa.Column("trade_type", sa.String(10)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("engagement_count", sa.Integer(), server_default="0"),
    )
    op.create_index("idx_social_post_user", "social_post", ["user_id", sa.text("created_at DESC")])

    # Social Comments
    op.create_table(
        "social_comment",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("social_post.id", ondelete="CASCADE")),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id")),
        sa.Column("content", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Social Likes
    op.create_table(
        "social_like",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("social_post.id", ondelete="CASCADE")),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id")),
        sa.Column("created_at", sa.DateTime()),
        sa.UniqueConstraint("post_id", "user_id", name="uq_social_like_post_user"),
    )

    # Watchlist
    op.create_table(
        "watchlist_item",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("portfolio_id", sa.Integer(), sa.ForeignKey("portfolio.id", ondelete="CASCADE")),
        sa.Column("stock_id", sa.Integer(), sa.ForeignKey("stock.id")),
        sa.Column("added_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("portfolio_id", "stock_id", name="uq_watchlist_portfolio_stock"),
    )


def downgrade() -> None:
    op.drop_table("watchlist_item")
    op.drop_table("social_like")
    op.drop_table("social_comment")
    op.drop_table("social_post")
    op.drop_table("user_module_progress")
    op.drop_table("learning_module")
    op.drop_table("trade")
    op.drop_table("holding")
    op.drop_table("portfolio")
    op.drop_table("risk_flag")
    op.drop_table("stock_prices")
    op.drop_table("stock_fundamentals")
    op.drop_table("stock")
    op.drop_table("user_risk_profile")
    op.drop_table("user")
