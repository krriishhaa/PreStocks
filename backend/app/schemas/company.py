from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class SectorBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_sector_id: Optional[int] = None
    color_hex: Optional[str] = None
    icon_name: Optional[str] = None

class SectorResponse(SectorBase):
    id: int
    class Config:
        from_attributes = True


class TagBase(BaseModel):
    name: str
    category: Optional[str] = None
    color_hex: Optional[str] = None

class TagResponse(TagBase):
    id: int
    class Config:
        from_attributes = True


class CompanyBase(BaseModel):
    ticker: Optional[str] = None
    name: str
    description: Optional[str] = None
    sector_id: Optional[int] = None
    industry: Optional[str] = None
    company_type: str = "public"

class CompanyCreate(CompanyBase):
    legal_name: Optional[str] = None
    website_url: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters_city: Optional[str] = None
    headquarters_country: Optional[str] = None
    exchange: Optional[str] = None

class CompanyListResponse(BaseModel):
    id: int
    ticker: Optional[str]
    name: str
    logo_url: Optional[str]
    sector_id: Optional[int]
    industry: Optional[str]
    market_cap: Optional[int]
    company_type: str
    exchange: Optional[str]
    class Config:
        from_attributes = True

class CompanyDetailResponse(BaseModel):
    id: int
    ticker: Optional[str]
    name: str
    legal_name: Optional[str]
    description: Optional[str]
    logo_url: Optional[str]
    website_url: Optional[str]
    sector_id: Optional[int]
    industry: Optional[str]
    sub_industry: Optional[str]
    founded_year: Optional[int]
    headquarters_city: Optional[str]
    headquarters_country: Optional[str]
    employee_count: Optional[int]
    ceo_name: Optional[str]
    market_cap: Optional[int]
    company_type: str
    exchange: Optional[str]
    ipo_date: Optional[date]
    is_active: bool
    created_at: Optional[datetime]
    class Config:
        from_attributes = True


class FundamentalsResponse(BaseModel):
    id: int
    company_id: int
    period_end: date
    period_type: str
    revenue: Optional[int]
    net_income: Optional[int]
    ebitda: Optional[int]
    gross_margin: Optional[float]
    operating_margin: Optional[float]
    net_margin: Optional[float]
    pe_ratio: Optional[float]
    price_to_sales: Optional[float]
    price_to_book: Optional[float]
    ev_to_ebitda: Optional[float]
    debt_to_equity: Optional[float]
    current_ratio: Optional[float]
    free_cash_flow: Optional[int]
    revenue_growth_yoy: Optional[float]
    earnings_growth_yoy: Optional[float]
    class Config:
        from_attributes = True


class InvestorBase(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None

class InvestorResponse(InvestorBase):
    id: int
    logo_url: Optional[str]
    headquarters_country: Optional[str]
    aum_usd: Optional[int]
    founded_year: Optional[int]
    notable_investments: Optional[List[str]]
    class Config:
        from_attributes = True


class FundingRoundResponse(BaseModel):
    id: int
    company_id: int
    round_type: str
    amount_raised_usd: Optional[int]
    pre_money_valuation: Optional[int]
    post_money_valuation: Optional[int]
    announced_date: Optional[date]
    lead_investor_id: Optional[int]
    num_investors: Optional[int]
    equity_dilution: Optional[float]
    class Config:
        from_attributes = True


class CompetitorResponse(BaseModel):
    id: int
    competitor_id: int
    competitor_name: Optional[str] = None
    competitor_ticker: Optional[str] = None
    overlap_score: Optional[float]
    relationship_type: Optional[str]
    category: Optional[str]
    class Config:
        from_attributes = True


class CompanySearchQuery(BaseModel):
    q: str = Field(..., min_length=1, max_length=100)
    sector_id: Optional[int] = None
    company_type: Optional[str] = None
    min_market_cap: Optional[int] = None
    max_market_cap: Optional[int] = None
    exchange: Optional[str] = None
    tags: Optional[List[int]] = None
    limit: int = Field(default=20, le=100)
    offset: int = 0
