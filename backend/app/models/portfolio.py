from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel
import enum


class OrderTypeEnum(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class Portfolio(BaseModel):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    name = Column(String(100), default="Main Portfolio")
    total_value = Column(Float, default=10000.00)
    cash_available = Column(Float, default=10000.00)
    initial_capital = Column(Float, default=10000.00)
    currency = Column(String(3), default="USD")
    is_default = Column(Boolean, default=True)
    strategy_notes = Column(Text)

    user = relationship("User", back_populates="portfolio")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="portfolio", cascade="all, delete-orphan")


class Holding(BaseModel):
    __tablename__ = "holding"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio.id", ondelete="CASCADE"))
    company_id = Column(Integer, ForeignKey("company.id"))
    quantity = Column(Float, nullable=False)
    average_buy_price = Column(Float, nullable=False)
    current_price = Column(Float)
    unrealized_pnl = Column(Float)
    unrealized_pnl_pct = Column(Float)
    weight_pct = Column(Float)

    portfolio = relationship("Portfolio", back_populates="holdings")
    company = relationship("Company", back_populates="holdings")


class Trade(BaseModel):
    __tablename__ = "trade"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio.id", ondelete="CASCADE"))
    company_id = Column(Integer, ForeignKey("company.id"))
    order_type = Column(String(10), nullable=False)
    order_method = Column(String(20), default="market")
    quantity = Column(Float, nullable=False)
    price_executed = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    limit_price = Column(Float)
    stop_price = Column(Float)
    commission = Column(Float, default=0)
    reasoning = Column(Text)
    risk_flags_at_trade = Column(JSONB)
    portfolio_snapshot = Column(JSONB)
    status = Column(String(20), default="executed")

    portfolio = relationship("Portfolio", back_populates="trades")
    company = relationship("Company")


class Watchlist(BaseModel):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False, default="My Watchlist")
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

    user = relationship("User", backref="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")


class WatchlistItem(BaseModel):
    __tablename__ = "watchlist_item"

    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey("watchlist.id", ondelete="CASCADE"))
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))
    notes = Column(Text)
    target_price = Column(Float)
    alert_above = Column(Float)
    alert_below = Column(Float)

    watchlist = relationship("Watchlist", back_populates="items")
    company = relationship("Company")
