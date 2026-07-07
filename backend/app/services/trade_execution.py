"""
Trade execution engine for paper trading.
Handles order validation, execution, and portfolio updates.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.portfolio import Portfolio, Holding, Trade
from app.models.stock import Stock
from app.utils.redis_cache import RedisCache
from app.utils.logger import logger


class TradeExecutionEngine:
    """Paper trading execution engine with full validation."""

    def __init__(self, db: AsyncSession, cache: Optional[RedisCache] = None):
        self.db = db
        self.cache = cache or RedisCache()

    async def place_order(self, portfolio_id: int, stock_id: int, quantity: float, order_type: str, limit_price: Optional[float] = None, order_details: Optional[dict] = None) -> Trade:
        """
        Execute a paper trade with full validation.

        Args:
            portfolio_id: The portfolio placing the order
            stock_id: Target stock
            quantity: Number of shares
            order_type: 'buy' or 'sell'
            limit_price: Optional limit price (market order if None)
            order_details: Full order ticket details for audit
        """
        portfolio = await self._get_portfolio(portfolio_id)
        stock = await self._get_stock(stock_id)
        current_price = await self._get_current_price(stock_id, stock.ticker)

        # Use limit price if specified, otherwise market price
        execution_price = limit_price if limit_price else current_price
        if execution_price <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to determine execution price")

        total_cost = quantity * execution_price

        # ─── VALIDATION ──────────────────────────────────────────────
        if order_type == "buy":
            if total_cost > portfolio.cash_available:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient cash. Need ${total_cost:,.2f} but only ${portfolio.cash_available:,.2f} available."
                )
        elif order_type == "sell":
            holding = await self._get_holding(portfolio_id, stock_id)
            if not holding or holding.quantity < quantity:
                available = holding.quantity if holding else 0
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient shares. Trying to sell {quantity} but only own {available}."
                )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="order_type must be 'buy' or 'sell'")

        # ─── EXECUTION (instant fill for paper trading) ──────────────
        trade = Trade(
            portfolio_id=portfolio_id,
            stock_id=stock_id,
            order_type=order_type,
            quantity=quantity,
            price_executed=execution_price,
            total_value=total_cost,
            executed_at=datetime.now(timezone.utc),
            order_ticket_details=order_details,
        )
        self.db.add(trade)

        # ─── UPDATE PORTFOLIO ────────────────────────────────────────
        if order_type == "buy":
            portfolio.cash_available -= total_cost
            await self._update_holding_buy(portfolio_id, stock_id, quantity, execution_price)
        else:
            portfolio.cash_available += total_cost
            await self._update_holding_sell(portfolio_id, stock_id, quantity)

        # Recalculate total portfolio value
        await self._recalculate_total_value(portfolio)

        await self.db.flush()

        logger.info(f"Trade executed: {order_type} {quantity} shares of {stock.ticker} @ ${execution_price:.2f}")

        return trade

    async def _update_holding_buy(self, portfolio_id: int, stock_id: int, quantity: float, price: float):
        """Add to existing holding or create new one. Recalculate average price."""
        holding = await self._get_holding(portfolio_id, stock_id)

        if holding:
            old_qty = holding.quantity
            old_avg = holding.average_buy_price
            new_qty = old_qty + quantity
            # Weighted average price
            holding.average_buy_price = ((old_avg * old_qty) + (price * quantity)) / new_qty
            holding.quantity = new_qty
            holding.updated_at = datetime.now(timezone.utc)
        else:
            holding = Holding(
                portfolio_id=portfolio_id,
                stock_id=stock_id,
                quantity=quantity,
                average_buy_price=price,
            )
            self.db.add(holding)

    async def _update_holding_sell(self, portfolio_id: int, stock_id: int, quantity: float):
        """Reduce or remove holding."""
        holding = await self._get_holding(portfolio_id, stock_id)
        if not holding:
            return

        holding.quantity -= quantity
        holding.updated_at = datetime.now(timezone.utc)

        if holding.quantity <= 0:
            await self.db.delete(holding)

    async def _recalculate_total_value(self, portfolio: Portfolio):
        """Recalculate total portfolio value from cash + holdings."""
        holdings_result = await self.db.execute(
            select(Holding).where(Holding.portfolio_id == portfolio.id)
        )
        holdings = holdings_result.scalars().all()

        holdings_value = 0.0
        for h in holdings:
            if h.quantity > 0:
                stock = await self._get_stock(h.stock_id)
                price = await self._get_current_price(h.stock_id, stock.ticker if stock else "")
                if price > 0:
                    holdings_value += h.quantity * price
                else:
                    holdings_value += h.quantity * h.average_buy_price

        portfolio.total_value = portfolio.cash_available + holdings_value
        portfolio.updated_at = datetime.now(timezone.utc)

    async def _get_portfolio(self, portfolio_id: int) -> Portfolio:
        result = await self.db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
        portfolio = result.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
        return portfolio

    async def _get_stock(self, stock_id: int) -> Stock:
        result = await self.db.execute(select(Stock).where(Stock.id == stock_id))
        stock = result.scalar_one_or_none()
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")
        return stock

    async def _get_holding(self, portfolio_id: int, stock_id: int) -> Optional[Holding]:
        result = await self.db.execute(
            select(Holding).where(Holding.portfolio_id == portfolio_id, Holding.stock_id == stock_id)
        )
        return result.scalar_one_or_none()

    async def _get_current_price(self, stock_id: int, ticker: str) -> float:
        """Get price from Redis cache first, then DB fallback."""
        if ticker:
            cached = await self.cache.get_price(ticker)
            if cached is not None:
                return cached

        # DB fallback
        from app.models.stock import StockPrice
        result = await self.db.execute(
            select(StockPrice).where(StockPrice.stock_id == stock_id).order_by(StockPrice.time.desc()).limit(1)
        )
        price_record = result.scalar_one_or_none()
        return price_record.close if price_record and price_record.close else 0.0
