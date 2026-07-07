from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel


class RiskFlag(BaseModel):
    __tablename__ = "risk_flag"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stock.id"))
    flag_type = Column(String(50), nullable=False)  # 'volatility', 'valuation', etc.
    severity_score = Column(Integer)  # 0-100
    explanation = Column(String(500))
    confidence_score = Column(Float)  # 0-1
    details = Column(JSON)  # Store additional context as JSON

    # Relationships
    stock = relationship("Stock")
