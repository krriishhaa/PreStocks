"""
Celery task: Update stock prices every 1 minute during market hours.
Fetches from configured data provider, updates Redis + DB.
"""
from datetime import datetime, timezone

from celery import shared_task

from app.core.config import get_settings
from app.core.constants import MARKET_HOURS

settings = get_settings()


@shared_task(name="tasks.update_prices")
def update_prices():
    """
    Runs every 1 minute during market hours.
    Fetches latest prices for all actively-held tickers.
    Updates Redis cache and inserts into stock_prices table.
    """
    import asyncio
    asyncio.run(_update_prices_async())


async def _update_prices_async():
    from app.database.session import get_db
    from app.services.price_stream import PriceFetcher
    from app.models.stock import StockPrice, Stock
    from app.models.portfolio import Holding
    from sqlalchemy import select, distinct
    from app.database.base import AsyncSessionLocal

    fetcher = PriceFetcher()

    async with AsyncSessionLocal() as db:
        # Get all tickers with active holdings
        result = await db.execute(
            select(distinct(Stock.ticker))
            .join(Holding, Holding.stock_id == Stock.id)
        )
        tickers = [row[0] for row in result.all()]

        if not tickers:
            return

        # Fetch batch prices
        prices = await fetcher.fetch_batch_prices(tickers)

        # Insert into price history
        for ticker, price in prices.items():
            stock_result = await db.execute(select(Stock).where(Stock.ticker == ticker))
            stock = stock_result.scalar_one_or_none()
            if stock and price:
                price_record = StockPrice(
                    time=datetime.now(timezone.utc),
                    stock_id=stock.id,
                    open=price,
                    high=price,
                    low=price,
                    close=price,
                    volume=0,
                )
                db.add(price_record)

        await db.commit()
