from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RiskFlagResponse(BaseModel):
    id: int
    stock_id: int
    flag_type: Optional[str] = None
    severity_score: Optional[int] = None
    explanation: Optional[str] = None
    confidence_score: Optional[float] = None
    calculated_at: datetime

    class Config:
        from_attributes = True


class CompositeScoreResponse(BaseModel):
    stock_id: int
    ticker: str
    overall_score: int
    severity: str
    flags: list[RiskFlagResponse] = []


class PortfolioRiskSummary(BaseModel):
    composite_risk: int
    severity: str
    concentration_warnings: list[str] = []
    diversification_score: float = 0.0
    explanation: str = ""
