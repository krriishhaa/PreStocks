"""
Celery task: Ingest news headlines hourly.
Runs FinBERT sentiment analysis and stores in vector DB.
"""
from celery import shared_task

from app.core.config import get_settings

settings = get_settings()


@shared_task(name="tasks.ingest_news")
def ingest_news():
    """
    Runs every hour.
    Fetches recent headlines for tracked tickers.
    Runs sentiment analysis (FinBERT).
    Stores results and updates vector embeddings.
    """
    import asyncio
    asyncio.run(_ingest_news_async())


async def _ingest_news_async():
    from datetime import datetime, timedelta, timezone
    from app.database.base import AsyncSessionLocal
    from app.models.stock import Stock
    from app.models.portfolio import Holding
    from app.utils.api_clients import FinnhubClient
    from app.ml_pipelines.sentiment import analyze_sentiment
    from app.ml_pipelines.embeddings import EmbeddingsStore
    from app.utils.redis_cache import RedisCache
    from app.utils.logger import logger
    from sqlalchemy import select, distinct

    cache = RedisCache()
    embeddings = EmbeddingsStore()
    await embeddings.initialize()

    async with AsyncSessionLocal() as db:
        # Get actively-held tickers
        result = await db.execute(
            select(distinct(Stock.ticker))
            .join(Holding, Holding.stock_id == Stock.id)
        )
        tickers = [row[0] for row in result.all()]

        if not tickers:
            return

        news_client = FinnhubClient()
        today = datetime.now(timezone.utc)
        from_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        to_date = today.strftime("%Y-%m-%d")

        for ticker in tickers:
            try:
                headlines = await news_client.get_news(ticker, from_date, to_date)

                for article in headlines[:10]:
                    title = article.get("headline", "")
                    if not title:
                        continue

                    # Run sentiment analysis
                    sentiment = await analyze_sentiment(title)

                    # Cache sentiment
                    await cache.set_json(
                        f"news_sentiment:{ticker}:{article.get('id', '')}",
                        {"title": title, "sentiment": sentiment.label, "confidence": sentiment.confidence},
                        ex=3600,
                    )

                    # Store in vector DB for context retrieval
                    await embeddings.add_document(
                        doc_id=f"{ticker}_{article.get('id', '')}",
                        text=title,
                        metadata={
                            "ticker": ticker,
                            "sentiment": sentiment.label,
                            "confidence": sentiment.confidence,
                            "published_at": article.get("datetime", ""),
                        },
                    )

            except Exception as e:
                logger.error(f"News ingestion failed for {ticker}: {e}")
