from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.flags import CompositeScoreResponse, PortfolioRiskSummary
from app.services.flag_service import FlagService
from app.core.security import get_current_user_id

router = APIRouter()


@router.get("/stock/{ticker}")
async def get_stock_flags(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    service = FlagService(db)
    return await service.get_flags_for_ticker(ticker.upper())


@router.get("/stock/{ticker}/score", response_model=CompositeScoreResponse)
async def get_composite_score(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    service = FlagService(db)
    return await service.get_composite_score(ticker.upper())


@router.get("/portfolio/risk-summary", response_model=PortfolioRiskSummary)
async def get_portfolio_risk(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = FlagService(db)
    return await service.get_portfolio_risk_summary(user_id)
