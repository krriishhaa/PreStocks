"""
Celery task: Ingest SEC EDGAR insider filings daily.
Updates insider activity data and triggers flag recalculation.
"""
from celery import shared_task

from app.core.config import get_settings

settings = get_settings()


@shared_task(name="tasks.ingest_insider_filings")
def ingest_insider_filings():
    """
    Runs daily (after market close).
    Fetches latest Form 4 filings from SEC EDGAR for tracked tickers.
    Updates stock_fundamentals table with net insider activity.
    Triggers flag recalculation if significant activity detected.
    """
    import asyncio
    asyncio.run(_ingest_filings_async())


async def _ingest_filings_async():
    from datetime import datetime, timedelta, timezone
    from app.database.base import AsyncSessionLocal
    from app.models.stock import Stock, StockFundamentals
    from app.models.portfolio import Holding
    from app.utils.logger import logger
    from sqlalchemy import select, distinct

    import httpx

    SEC_EDGAR_BASE = "https://efts.sec.gov/LATEST/search-index"
    INSIDER_THRESHOLD = 50000  # $50k in transactions triggers flag

    async with AsyncSessionLocal() as db:
        # Get actively-held tickers
        result = await db.execute(
            select(distinct(Stock.ticker))
            .join(Holding, Holding.stock_id == Stock.id)
        )
        tickers = [row[0] for row in result.all()]

        for ticker in tickers:
            try:
                # In production, query SEC EDGAR XBRL API for Form 4 filings
                # For now, simulate the logic:
                #
                # async with httpx.AsyncClient() as client:
                #     resp = await client.get(
                #         f"https://www.sec.gov/cgi-bin/browse-edgar",
                #         params={
                #             "action": "getcompany",
                #             "company": ticker,
                #             "type": "4",
                #             "dateb": "",
                #             "owner": "include",
                #             "count": "10",
                #             "output": "atom",
                #         }
                #     )
                #     filings = parse_form4_filings(resp.text)
                #
                #     net_shares = sum(f.shares_delta for f in filings)
                #     net_value = sum(f.value_delta for f in filings)
                #
                #     # Update fundamentals
                #     stock_result = await db.execute(
                #         select(Stock).where(Stock.ticker == ticker)
                #     )
                #     stock = stock_result.scalar_one_or_none()
                #     if stock:
                #         # Update or create fundamentals record
                #         ...
                #
                #     # Trigger recalculation if significant
                #     if abs(net_value) > INSIDER_THRESHOLD:
                #         from app.tasks.calculate_flags import recalculate_single_ticker
                #         recalculate_single_ticker.delay(ticker)

                pass  # Placeholder until SEC EDGAR integration

            except Exception as e:
                logger.error(f"Insider filing ingestion failed for {ticker}: {e}")

        await db.commit()
