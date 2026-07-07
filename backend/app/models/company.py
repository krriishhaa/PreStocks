from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, BigInteger, Date, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel


class Company(BaseModel):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, index=True)
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255))
    description = Column(Text)
    logo_url = Column(Text)
    website_url = Column(Text)
    sector_id = Column(Integer, ForeignKey("sector.id"))
    industry = Column(String(150))
    sub_industry = Column(String(150))
    founded_year = Column(Integer)
    headquarters_city = Column(String(100))
    headquarters_country = Column(String(100))
    employee_count = Column(Integer)
    ceo_name = Column(String(255))
    market_cap = Column(BigInteger)
    company_type = Column(String(30), default="public")
    exchange = Column(String(20))
    ipo_date = Column(Date)
    is_active = Column(Boolean, default=True)
    metadata_ = Column("metadata", JSONB, default={})

    sector = relationship("Sector", back_populates="companies")
    tags = relationship("Tag", secondary="company_tag", lazy="selectin")
    fundamentals = relationship("CompanyFundamentals", back_populates="company", order_by="CompanyFundamentals.period_end.desc()")
    funding_rounds = relationship("FundingRound", back_populates="company", order_by="FundingRound.announced_date.desc()")
    risk_flags = relationship("RiskFlag", back_populates="company")
    holdings = relationship("Holding", back_populates="company")
    news_articles = relationship("NewsArticle", secondary="news_company", lazy="dynamic")
    competitors = relationship("CompetitorRelationship", foreign_keys="CompetitorRelationship.company_id", back_populates="company")
    research_reports = relationship("AIResearchReport", back_populates="company")


class CompanyTag(Base):
    __tablename__ = "company_tag"

    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True)


class CompanyFundamentals(BaseModel):
    __tablename__ = "company_fundamentals"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))
    period_end = Column(Date, nullable=False)
    period_type = Column(String(10), default="quarterly")
    revenue = Column(BigInteger)
    net_income = Column(BigInteger)
    ebitda = Column(BigInteger)
    gross_margin = Column(Float)
    operating_margin = Column(Float)
    net_margin = Column(Float)
    pe_ratio = Column(Float)
    price_to_sales = Column(Float)
    price_to_book = Column(Float)
    ev_to_ebitda = Column(Float)
    debt_to_equity = Column(Float)
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    interest_coverage = Column(Float)
    free_cash_flow = Column(BigInteger)
    cash_and_equivalents = Column(BigInteger)
    total_debt = Column(BigInteger)
    shares_outstanding = Column(BigInteger)
    dividend_yield = Column(Float)
    payout_ratio = Column(Float)
    roe = Column(Float)
    roa = Column(Float)
    revenue_growth_yoy = Column(Float)
    earnings_growth_yoy = Column(Float)
    cash_runway_months = Column(Integer)

    company = relationship("Company", back_populates="fundamentals")


class CompetitorRelationship(BaseModel):
    __tablename__ = "competitor_relationship"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))
    competitor_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))
    overlap_score = Column(Float)
    relationship_type = Column(String(30))
    category = Column(String(50))
    source = Column(String(50))

    company = relationship("Company", foreign_keys=[company_id], back_populates="competitors")
    competitor = relationship("Company", foreign_keys=[competitor_id])
