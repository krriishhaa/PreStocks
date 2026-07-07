from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.company import Company, CompanyFundamentals, CompetitorRelationship
from app.models.investor import FundingRound, FundingRoundInvestor, Investor
from app.models.sector import Sector, Tag
from app.models.flags import RiskFlag
from app.schemas.company import (
    CompanyListResponse, CompanyDetailResponse, CompanySearchQuery,
    FundamentalsResponse, FundingRoundResponse, InvestorResponse,
    CompetitorResponse, SectorResponse, TagResponse
)

router = APIRouter()


@router.get("/search", response_model=List[CompanyListResponse])
def search_companies(
    q: str = Query(..., min_length=1),
    sector_id: Optional[int] = None,
    company_type: Optional[str] = None,
    min_market_cap: Optional[int] = None,
    max_market_cap: Optional[int] = None,
    exchange: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Company).filter(Company.is_active == True)

    query = query.filter(
        or_(
            Company.name.ilike(f"%{q}%"),
            Company.ticker.ilike(f"%{q}%"),
            Company.industry.ilike(f"%{q}%")
        )
    )

    if sector_id:
        query = query.filter(Company.sector_id == sector_id)
    if company_type:
        query = query.filter(Company.company_type == company_type)
    if min_market_cap:
        query = query.filter(Company.market_cap >= min_market_cap)
    if max_market_cap:
        query = query.filter(Company.market_cap <= max_market_cap)
    if exchange:
        query = query.filter(Company.exchange == exchange)

    return query.offset(offset).limit(limit).all()


@router.get("/{company_id}", response_model=CompanyDetailResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/{company_id}/fundamentals", response_model=List[FundamentalsResponse])
def get_fundamentals(
    company_id: int,
    period_type: str = "quarterly",
    limit: int = Query(default=8, le=40),
    db: Session = Depends(get_db)
):
    return (
        db.query(CompanyFundamentals)
        .filter(CompanyFundamentals.company_id == company_id)
        .filter(CompanyFundamentals.period_type == period_type)
        .order_by(CompanyFundamentals.period_end.desc())
        .limit(limit)
        .all()
    )


@router.get("/{company_id}/funding-rounds", response_model=List[FundingRoundResponse])
def get_funding_rounds(company_id: int, db: Session = Depends(get_db)):
    return (
        db.query(FundingRound)
        .filter(FundingRound.company_id == company_id)
        .order_by(FundingRound.announced_date.desc())
        .all()
    )


@router.get("/{company_id}/competitors", response_model=List[CompetitorResponse])
def get_competitors(company_id: int, db: Session = Depends(get_db)):
    rels = (
        db.query(CompetitorRelationship)
        .filter(CompetitorRelationship.company_id == company_id)
        .order_by(CompetitorRelationship.overlap_score.desc())
        .all()
    )
    result = []
    for rel in rels:
        comp = db.query(Company).filter(Company.id == rel.competitor_id).first()
        result.append(CompetitorResponse(
            id=rel.id,
            competitor_id=rel.competitor_id,
            competitor_name=comp.name if comp else None,
            competitor_ticker=comp.ticker if comp else None,
            overlap_score=rel.overlap_score,
            relationship_type=rel.relationship_type,
            category=rel.category
        ))
    return result


@router.get("/{company_id}/risk-flags")
def get_company_risk_flags(company_id: int, db: Session = Depends(get_db)):
    flags = (
        db.query(RiskFlag)
        .filter(RiskFlag.company_id == company_id, RiskFlag.is_active == True)
        .order_by(RiskFlag.severity_score.desc())
        .all()
    )
    return flags


@router.get("/sectors/", response_model=List[SectorResponse])
def list_sectors(db: Session = Depends(get_db)):
    return db.query(Sector).all()


@router.get("/tags/", response_model=List[TagResponse])
def list_tags(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Tag)
    if category:
        query = query.filter(Tag.category == category)
    return query.all()
