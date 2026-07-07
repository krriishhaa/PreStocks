from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class AIResearchRequest(BaseModel):
    company_id: Optional[int] = None
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    report_type: str = Field(default="full_analysis", pattern="^(full_analysis|risk_assessment|competitor_map|ipo_probability|swot)$")
    include_sections: List[str] = Field(
        default=["summary", "risks", "opportunities", "financial_health", "funding_history", "competitors", "ipo_probability"]
    )

class AIResearchResponse(BaseModel):
    id: int
    company_id: Optional[int]
    report_type: str
    summary: Optional[str]
    risks: Optional[List[dict]]
    opportunities: Optional[List[dict]]
    financial_health: Optional[dict]
    funding_history: Optional[dict]
    competitors: Optional[List[dict]]
    ipo_probability: Optional[dict]
    swot_analysis: Optional[dict]
    model_used: Optional[str]
    data_sources: Optional[List[str]]
    confidence_score: Optional[float]
    generation_time_ms: Optional[int]
    created_at: Optional[datetime]
    class Config:
        from_attributes = True


class PortfolioAdviceRequest(BaseModel):
    portfolio_id: Optional[int] = None
    advice_type: str = Field(default="weekly_review", pattern="^(weekly_review|rebalance|diversification|risk_alert)$")

class PortfolioAdviceResponse(BaseModel):
    id: int
    portfolio_id: Optional[int]
    advice_type: str
    overall_health_score: Optional[int]
    diversification_score: Optional[int]
    concentration_risk: Optional[dict]
    missing_sectors: Optional[List[str]]
    suggestions: Optional[List[dict]]
    portfolio_snapshot: Optional[dict]
    model_used: Optional[str]
    created_at: Optional[datetime]
    class Config:
        from_attributes = True


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    company_id: Optional[int] = None
    context_type: str = Field(default="general", pattern="^(general|research|portfolio_advice|flag_explain)$")

class AIChatResponse(BaseModel):
    conversation_id: str
    message: str
    model_used: Optional[str]
    tokens_used: Optional[int]
    latency_ms: Optional[int]
    sources: Optional[List[str]] = []


class AIPromptTemplateResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    model: str
    version: int
    is_active: bool
    class Config:
        from_attributes = True
