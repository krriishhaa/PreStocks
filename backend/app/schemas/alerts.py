from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class AlertCreate(BaseModel):
    company_id: Optional[int] = None
    alert_type: str = Field(..., pattern="^(price_above|price_below|risk_flag|news|earnings|funding_round|portfolio_threshold)$")
    condition: dict
    title: Optional[str] = None
    message: Optional[str] = None
    cooldown_hours: int = 24

class AlertUpdate(BaseModel):
    is_active: Optional[bool] = None
    condition: Optional[dict] = None
    title: Optional[str] = None
    cooldown_hours: Optional[int] = None

class AlertResponse(BaseModel):
    id: int
    user_id: int
    company_id: Optional[int]
    alert_type: str
    condition: dict
    title: Optional[str]
    message: Optional[str]
    is_active: bool
    is_triggered: bool
    triggered_at: Optional[datetime]
    cooldown_hours: int
    created_at: Optional[datetime]
    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    message: str
    metadata: Optional[dict] = {}
    channel: str
    is_read: bool
    read_at: Optional[datetime]
    created_at: Optional[datetime]
    class Config:
        from_attributes = True


class WatchlistCreate(BaseModel):
    name: str = Field(default="My Watchlist", max_length=100)
    description: Optional[str] = None

class WatchlistItemAdd(BaseModel):
    company_id: int
    notes: Optional[str] = None
    target_price: Optional[float] = None
    alert_above: Optional[float] = None
    alert_below: Optional[float] = None

class WatchlistResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    is_default: bool
    items_count: int = 0
    created_at: Optional[datetime]
    class Config:
        from_attributes = True

class WatchlistItemResponse(BaseModel):
    id: int
    watchlist_id: int
    company_id: int
    company_name: Optional[str] = None
    company_ticker: Optional[str] = None
    notes: Optional[str]
    target_price: Optional[float]
    alert_above: Optional[float]
    alert_below: Optional[float]
    added_at: Optional[datetime]
    class Config:
        from_attributes = True


class NewsResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    source_name: Optional[str]
    article_url: str
    image_url: Optional[str]
    author: Optional[str]
    published_at: datetime
    category: Optional[str]
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    is_breaking: bool = False
    class Config:
        from_attributes = True
