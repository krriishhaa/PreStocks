from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel


class RiskFlag(BaseModel):
    __tablename__ = "risk_flag"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))
    flag_type = Column(String(50), nullable=False)
    severity_score = Column(Integer)
    title = Column(String(255))
    explanation = Column(Text)
    ai_explanation = Column(Text)
    confidence_score = Column(Float)
    data_sources = Column(ARRAY(Text))
    raw_data = Column(JSONB)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)

    company = relationship("Company", back_populates="risk_flags")


class CompositeRiskScore(BaseModel):
    __tablename__ = "composite_risk_score"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))
    overall_score = Column(Integer)
    volatility_component = Column(Integer)
    valuation_component = Column(Integer)
    financial_health_component = Column(Integer)
    momentum_component = Column(Integer)
    insider_component = Column(Integer)
    sentiment_component = Column(Integer)
    weights = Column(JSONB)

    company = relationship("Company")
