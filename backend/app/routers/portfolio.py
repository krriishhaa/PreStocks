from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.portfolio import PortfolioResponse, PortfolioSummary
from app.schemas.trade import OrderCreate, OrderResponse, TradeHistoryItem
from app.services.portfolio_service import PortfolioService
from app.core.security import get_current_user_id
from app.core.tier_gate import require_beginner

router = APIRouter()


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = PortfolioService(db)
    return await service.get_portfolio(user_id)


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = PortfolioService(db)
    return await service.get_summary(user_id)


@router.post("/trades", response_model=OrderResponse)
async def place_trade(
    order: OrderCreate,
    user_id: int = Depends(require_beginner),
    db: AsyncSession = Depends(get_db),
):
    """Place a trade. Requires at least Beginner tier (completed onboarding)."""
    service = PortfolioService(db)
    return await service.execute_trade(user_id, order)


@router.get("/trades", response_model=list[TradeHistoryItem])
async def get_trade_history(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, le=100),
):
    service = PortfolioService(db)
    return await service.get_trade_history(user_id, limit)


@router.get("/risk-summary")
async def get_portfolio_risk_summary(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from app.services.flag_service import FlagService
    service = FlagService(db)
    return await service.get_portfolio_risk_summary(user_id)
