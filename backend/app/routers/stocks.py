from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.stock import StockDetailResponse, StockSearchResult, PricePoint
from app.services.stock_service import StockService
from app.core.security import get_current_user_id

router = APIRouter()


@router.get("/search", response_model=list[StockSearchResult])
async def search_stocks(
    q: str = Query(min_length=1, max_length=20),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    service = StockService(db)
    return await service.search(q, limit)


@router.get("/{ticker}", response_model=StockDetailResponse)
async def get_stock(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    service = StockService(db)
    return await service.get_stock_detail(ticker.upper())


@router.get("/{ticker}/flags")
async def get_stock_flags(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    from app.services.flag_service import FlagService
    service = FlagService(db)
    return await service.get_flags_for_ticker(ticker.upper())


@router.get("/{ticker}/prices", response_model=list[PricePoint])
async def get_price_history(
    ticker: str,
    timeframe: str = Query(default="1M", pattern="^(1D|1W|1M|6M|1Y)$"),
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    service = StockService(db)
    return await service.get_price_history(ticker.upper(), timeframe)


@router.post("/{ticker}/flags/{flag_type}/explain")
async def explain_flag(
    ticker: str,
    flag_type: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Run the LangGraph flag explainer agent.
    Returns a plain-English explanation + guidance tailored to user tier.
    Cached in Redis for 1 hour.
    """
    from app.utils.redis_cache import RedisCache
    from app.services.user_service import UserService
    from app.agents.flag_explainer import explain_flag_for_user
    from app.models.stock import Stock
    from sqlalchemy import select

    cache = RedisCache()
    cache_key = f"explain:{ticker}:{flag_type}:{user_id}"
    cached = await cache.get_json(cache_key)
    if cached:
        return cached

    # Get user tier
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    user_tier = user.risk_tier if user and user.risk_tier else "beginner"

    # Get stock_id
    result = await db.execute(select(Stock).where(Stock.ticker == ticker.upper()))
    stock = result.scalar_one_or_none()
    stock_id = stock.id if stock else 0

    explanation = await explain_flag_for_user(stock_id, flag_type, user_tier)

    # Cache for 1 hour
    await cache.set_json(cache_key, explanation, ex=3600)

    return explanation
