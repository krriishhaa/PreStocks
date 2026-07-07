from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HoldingResponse(BaseModel):
    id: int
    stock_id: int
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    quantity: float
    average_buy_price: float
    current_price: float = 0.0
    total_value: float = 0.0
    gain_loss_pct: float = 0.0
    sector: Optional[str] = None

    class Config:
        from_attributes = True


class PortfolioResponse(BaseModel):
    id: int
    total_value: float
    cash_available: float
    holdings: list[HoldingResponse] = []

    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    total_value: float
    cash_available: float
    holdings_count: int
    sectors_count: int
    cash_percent: float


class WatchlistItemResponse(BaseModel):
    id: int
    stock_id: int
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    added_at: datetime

    class Config:
        from_attributes = True
