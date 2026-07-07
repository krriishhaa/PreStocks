from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel
import uuid


class AIPromptTemplate(BaseModel):
    __tablename__ = "ai_prompt_template"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text, nullable=False)
    model = Column(String(50), default="claude-sonnet-4-20250514")
    temperature = Column(Float, default=0.3)
    max_tokens = Column(Integer, default=2000)
    input_schema = Column(JSONB)
    output_schema = Column(JSONB)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)


class AIConversation(BaseModel):
    __tablename__ = "ai_conversation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    company_id = Column(Integer, ForeignKey("company.id"))
    context_type = Column(String(50))
    title = Column(String(255))
    metadata_ = Column("metadata", JSONB, default={})

    user = relationship("User", backref="ai_conversations")
    company = relationship("Company")
    messages = relationship("AIMessage", back_populates="conversation", order_by="AIMessage.created_at")


class AIMessage(BaseModel):
    __tablename__ = "ai_message"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("ai_conversation.id", ondelete="CASCADE"))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    prompt_template_id = Column(Integer, ForeignKey("ai_prompt_template.id"))
    model_used = Column(String(50))
    tokens_input = Column(Integer)
    tokens_output = Column(Integer)
    latency_ms = Column(Integer)
    cost_usd = Column(Float)
    metadata_ = Column("metadata", JSONB, default={})

    conversation = relationship("AIConversation", back_populates="messages")
    prompt_template = relationship("AIPromptTemplate")


class AIResearchReport(BaseModel):
    __tablename__ = "ai_research_report"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    company_id = Column(Integer, ForeignKey("company.id"))
    report_type = Column(String(50), nullable=False)
    summary = Column(Text)
    risks = Column(JSONB)
    opportunities = Column(JSONB)
    financial_health = Column(JSONB)
    funding_history = Column(JSONB)
    competitors = Column(JSONB)
    ipo_probability = Column(JSONB)
    swot_analysis = Column(JSONB)
    raw_response = Column(Text)
    model_used = Column(String(50))
    data_sources = Column(ARRAY(Text))
    confidence_score = Column(Float)
    is_stale = Column(Boolean, default=False)
    valid_until = Column(DateTime)
    generation_time_ms = Column(Integer)

    user = relationship("User", backref="research_reports")
    company = relationship("Company", back_populates="research_reports")


class AIPortfolioAdvice(BaseModel):
    __tablename__ = "ai_portfolio_advice"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    portfolio_id = Column(Integer, ForeignKey("portfolio.id"))
    advice_type = Column(String(50), nullable=False)
    overall_health_score = Column(Integer)
    diversification_score = Column(Integer)
    concentration_risk = Column(JSONB)
    missing_sectors = Column(JSONB)
    suggestions = Column(JSONB)
    portfolio_snapshot = Column(JSONB)
    model_used = Column(String(50))
    is_read = Column(Boolean, default=False)

    user = relationship("User", backref="portfolio_advices")
    portfolio = relationship("Portfolio")
