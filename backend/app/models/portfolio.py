"""
Portfolio model — holds user portfolio state, holdings, and trade history.
Column names are consistent with what the router uses.
"""
from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import BaseModel


class Portfolio(BaseModel):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True)
    name = Column(String(100), default="Main Portfolio")
    cash = Column(Float, default=10000.00, nullable=False)
    initial_capital = Column(Float, default=10000.00, nullable=False)
    currency = Column(String(3), default="USD")
    is_default = Column(Boolean, default=True)

    user = relationship("User", back_populates="portfolio")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="portfolio", cascade="all, delete-orphan", order_by="Trade.executed_at.desc()")


class Holding(BaseModel):
    __tablename__ = "holding"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio.id", ondelete="CASCADE"))
    symbol = Column(String(10), nullable=False)
    company_name = Column(String(255))
    shares = Column(Float, nullable=False)
    avg_buy_price = Column(Float, nullable=False)
    current_price = Column(Float)

    portfolio = relationship("Portfolio", back_populates="holdings")

    @property
    def market_value(self):
        return self.shares * (self.current_price or self.avg_buy_price)

    @property
    def unrealized_pnl(self):
        if not self.current_price:
            return 0.0
        return (self.current_price - self.avg_buy_price) * self.shares

    @property
    def unrealized_pnl_pct(self):
        if not self.current_price or self.avg_buy_price == 0:
            return 0.0
        return ((self.current_price - self.avg_buy_price) / self.avg_buy_price) * 100


class Trade(BaseModel):
    __tablename__ = "trade"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio.id", ondelete="CASCADE"))
    symbol = Column(String(10), nullable=False)
    company_name = Column(String(255))
    side = Column(String(4), nullable=False)  # 'buy' or 'sell'
    order_type = Column(String(20), default="market")
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), default="filled")
    executed_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    portfolio = relationship("Portfolio", back_populates="trades")


class Watchlist(BaseModel):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False, default="My Watchlist")
    is_default = Column(Boolean, default=True)

    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")


class WatchlistItem(BaseModel):
    __tablename__ = "watchlist_item"

    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey("watchlist.id", ondelete="CASCADE"))
    symbol = Column(String(10), nullable=False)
    company_name = Column(String(255))
    added_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    watchlist = relationship("Watchlist", back_populates="items")
