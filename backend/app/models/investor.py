from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, BigInteger, Date, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel


class Investor(BaseModel):
    __tablename__ = "investor"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))
    description = Column(Text)
    logo_url = Column(Text)
    website_url = Column(Text)
    headquarters_city = Column(String(100))
    headquarters_country = Column(String(100))
    aum_usd = Column(BigInteger)
    founded_year = Column(Integer)
    notable_investments = Column(ARRAY(Text))
    investment_stages = Column(ARRAY(Text))
    sectors_focus = Column(ARRAY(Integer))
    is_active = Column(Boolean, default=True)
    metadata_ = Column("metadata", JSONB, default={})

    funding_participations = relationship("FundingRoundInvestor", back_populates="investor")


class FundingRound(BaseModel):
    __tablename__ = "funding_round"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"))
    round_type = Column(String(50), nullable=False)
    amount_raised_usd = Column(BigInteger)
    pre_money_valuation = Column(BigInteger)
    post_money_valuation = Column(BigInteger)
    announced_date = Column(Date)
    closed_date = Column(Date)
    lead_investor_id = Column(Integer, ForeignKey("investor.id"))
    num_investors = Column(Integer)
    equity_dilution = Column(Float)
    source_url = Column(Text)
    notes = Column(Text)
    metadata_ = Column("metadata", JSONB, default={})

    company = relationship("Company", back_populates="funding_rounds")
    lead_investor = relationship("Investor", foreign_keys=[lead_investor_id])
    investors = relationship("FundingRoundInvestor", back_populates="funding_round")


class FundingRoundInvestor(Base):
    __tablename__ = "funding_round_investor"

    funding_round_id = Column(Integer, ForeignKey("funding_round.id", ondelete="CASCADE"), primary_key=True)
    investor_id = Column(Integer, ForeignKey("investor.id", ondelete="CASCADE"), primary_key=True)
    amount_invested_usd = Column(BigInteger)
    is_lead = Column(Boolean, default=False)

    funding_round = relationship("FundingRound", back_populates="investors")
    investor = relationship("Investor", back_populates="funding_participations")
