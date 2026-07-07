from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    ticker: str = Field(max_length=10)
    order_type: str = Field(pattern="^(buy|sell)$")
    quantity: float = Field(gt=0)
    limit_price: Optional[float] = None
    order_ticket_details: Optional[dict] = None


class OrderResponse(BaseModel):
    id: int
    stock_id: int
    order_type: Optional[str] = None
    quantity: float
    price_executed: float
    total_value: float
    executed_at: datetime
    status: str = "filled"

    class Config:
        from_attributes = True


class TradeHistoryItem(BaseModel):
    id: int
    ticker: str
    order_type: Optional[str] = None
    quantity: float
    price_executed: float
    total_value: float
    executed_at: datetime

    class Config:
        from_attributes = True
