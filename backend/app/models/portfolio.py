from sqlalchemy import Column, Integer, Float, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel
import enum


class OrderTypeEnum(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class Portfolio(BaseModel):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True)
    total_value = Column(Float, default=10000.00)
    cash_available = Column(Float, default=10000.00)

    # Relationships
    user = relationship("User", back_populates="portfolio")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="portfolio", cascade="all, delete-orphan")


class Holding(BaseModel):
    __tablename__ = "holding"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio.id", ondelete="CASCADE"))
    stock_id = Column(Integer, ForeignKey("stock.id"))
    quantity = Column(Float, nullable=False)
    average_buy_price = Column(Float, nullable=False)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    stock = relationship("Stock")


class Trade(BaseModel):
    __tablename__ = "trade"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio.id", ondelete="CASCADE"))
    stock_id = Column(Integer, ForeignKey("stock.id"))
    order_type = Column(String(10))  # 'buy' or 'sell'
    quantity = Column(Float, nullable=False)
    price_executed = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    order_ticket_details = Column(JSON)  # Store order details as JSON

    # Relationships
    portfolio = relationship("Portfolio", back_populates="trades")
    stock = relationship("Stock")
