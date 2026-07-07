from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.stock import Stock, StockFundamentals, StockPrice
from app.schemas.stock import StockDetailResponse, StockSearchResult, PricePoint


class StockService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(self, query: str, limit: int = 10) -> list[StockSearchResult]:
        result = await self.db.execute(
            select(Stock)
            .where(Stock.ticker.ilike(f"%{query}%") | Stock.company_name.ilike(f"%{query}%"))
            .limit(limit)
        )
        stocks = result.scalars().all()
        return [StockSearchResult(id=s.id, ticker=s.ticker, company_name=s.company_name, sector=s.sector) for s in stocks]

    async def get_stock_detail(self, ticker: str) -> StockDetailResponse:
        result = await self.db.execute(select(Stock).where(Stock.ticker == ticker))
        stock = result.scalar_one_or_none()
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock {ticker} not found")

        fund_result = await self.db.execute(
            select(StockFundamentals)
            .where(StockFundamentals.stock_id == stock.id)
            .order_by(StockFundamentals.updated_at.desc())
            .limit(1)
        )
        fundamentals = fund_result.scalar_one_or_none()

        price_result = await self.db.execute(
            select(StockPrice)
            .where(StockPrice.stock_id == stock.id)
            .order_by(StockPrice.time.desc())
            .limit(1)
        )
        latest_price = price_result.scalar_one_or_none()

        return StockDetailResponse(
            id=stock.id,
            ticker=stock.ticker,
            company_name=stock.company_name,
            sector=stock.sector,
            industry=stock.industry,
            market_cap=stock.market_cap,
            current_price=latest_price.close if latest_price else 0.0,
            change_pct=0.0,
            pe_ratio=fundamentals.pe_ratio if fundamentals else None,
            price_to_sales=fundamentals.price_to_sales if fundamentals else None,
            debt_to_equity=fundamentals.debt_to_equity if fundamentals else None,
            current_ratio=fundamentals.current_ratio if fundamentals else None,
            interest_coverage=fundamentals.interest_coverage if fundamentals else None,
            cash_runway_months=fundamentals.cash_runway_months if fundamentals else None,
        )

    async def get_price_history(self, ticker: str, timeframe: str) -> list[PricePoint]:
        stock_result = await self.db.execute(select(Stock).where(Stock.ticker == ticker))
        stock = stock_result.scalar_one_or_none()
        if not stock:
            return []

        now = datetime.now(timezone.utc)
        delta_map = {"1D": timedelta(days=1), "1W": timedelta(weeks=1), "1M": timedelta(days=30), "6M": timedelta(days=180), "1Y": timedelta(days=365)}
        start = now - delta_map.get(timeframe, timedelta(days=30))

        result = await self.db.execute(
            select(StockPrice)
            .where(StockPrice.stock_id == stock.id, StockPrice.time >= start)
            .order_by(StockPrice.time.asc())
        )
        prices = result.scalars().all()
        return [PricePoint(time=p.time, open=p.open, high=p.high, low=p.low, close=p.close, volume=p.volume) for p in prices]
