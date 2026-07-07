"""
Celery task: Recalculate risk flags every 5 minutes during market hours.
Uses the FlagCalculationEngine for full composite scoring.
"""
from celery import shared_task

from app.core.config import get_settings

settings = get_settings()


@shared_task(name="tasks.calculate_flags")
def calculate_flags():
    """
    Runs every 5 minutes during market hours.
    Recalculates composite risk scores for all actively-held tickers.
    Stores results in DB and Redis cache (TTL 300s).
    """
    import asyncio
    asyncio.run(_calculate_flags_async())


@shared_task(name="tasks.recalculate_single_ticker")
def recalculate_single_ticker(ticker: str):
    """Triggered when a stock moves >2%. Recalculates immediately."""
    import asyncio
    asyncio.run(_recalculate_ticker_async(ticker))


async def _calculate_flags_async():
    from app.database.base import AsyncSessionLocal
    from app.models.stock import Stock
    from app.models.portfolio import Holding
    from app.services.flag_calculation_engine import FlagCalculationEngine
    from app.utils.redis_cache import RedisCache
    from sqlalchemy import select, distinct

    cache = RedisCache()

    async with AsyncSessionLocal() as db:
        # Get all tickers with active holdings
        result = await db.execute(
            select(distinct(Holding.stock_id))
        )
        stock_ids = [row[0] for row in result.all()]

        engine = FlagCalculationEngine(db, cache)

        for stock_id in stock_ids:
            try:
                await engine.compute_and_store(stock_id)
            except Exception as e:
                from app.utils.logger import logger
                logger.error(f"Flag calculation failed for stock_id={stock_id}: {e}")

        await db.commit()


async def _recalculate_ticker_async(ticker: str):
    from app.database.base import AsyncSessionLocal
    from app.models.stock import Stock
    from app.services.flag_calculation_engine import FlagCalculationEngine
    from app.utils.redis_cache import RedisCache
    from sqlalchemy import select

    cache = RedisCache()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Stock).where(Stock.ticker == ticker))
        stock = result.scalar_one_or_none()
        if not stock:
            return

        engine = FlagCalculationEngine(db, cache)
        await engine.compute_and_store(stock.id)
        await db.commit()
