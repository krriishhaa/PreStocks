from sqlalchemy import Column, Integer, String, Float, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel


class Stock(BaseModel):
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, index=True, nullable=False)
    company_name = Column(String(255))
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(BigInteger)

    # Relationships
    fundamentals = relationship("StockFundamentals", back_populates="stock")


class StockFundamentals(BaseModel):
    __tablename__ = "stock_fundamentals"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stock.id"))
    quarter_date = Column(String(10))  # YYYY-Q# format
    pe_ratio = Column(Float)
    price_to_sales = Column(Float)
    debt_to_equity = Column(Float)
    current_ratio = Column(Float)
    interest_coverage = Column(Float)
    cash_runway_months = Column(Integer)

    # Relationships
    stock = relationship("Stock", back_populates="fundamentals")


from sqlalchemy import ForeignKey
