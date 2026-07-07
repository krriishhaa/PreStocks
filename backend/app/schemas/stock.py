from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StockResponse(BaseModel):
    id: int
    ticker: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[int] = None

    class Config:
        from_attributes = True


class StockDetailResponse(BaseModel):
    id: int
    ticker: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[int] = None
    current_price: float = 0.0
    change_pct: float = 0.0
    pe_ratio: Optional[float] = None
    price_to_sales: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    interest_coverage: Optional[float] = None
    cash_runway_months: Optional[int] = None


class StockSearchResult(BaseModel):
    id: int
    ticker: str
    company_name: Optional[str] = None
    sector: Optional[str] = None


class PricePoint(BaseModel):
    time: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None
