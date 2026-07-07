from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.portfolio import Portfolio, Holding, Trade, WatchlistItem
from app.models.stock import Stock, StockPrice
from app.schemas.portfolio import PortfolioResponse, PortfolioSummary, HoldingResponse
from app.schemas.trade import OrderCreate, OrderResponse, TradeHistoryItem


class PortfolioService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_portfolio(self, user_id: int) -> PortfolioResponse:
        result = await self.db.execute(
            select(Portfolio)
            .options(selectinload(Portfolio.holdings))
            .where(Portfolio.user_id == user_id)
        )
        portfolio = result.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

        holdings = []
        for h in portfolio.holdings:
            stock = await self._get_stock(h.stock_id)
            current_price = await self._get_current_price(h.stock_id)
            total_value = h.quantity * current_price
            gain_loss = ((current_price - h.average_buy_price) / h.average_buy_price * 100) if h.average_buy_price > 0 else 0

            holdings.append(HoldingResponse(
                id=h.id, stock_id=h.stock_id,
                ticker=stock.ticker if stock else "???",
                company_name=stock.company_name if stock else None,
                quantity=h.quantity, average_buy_price=h.average_buy_price,
                current_price=current_price, total_value=total_value,
                gain_loss_pct=round(gain_loss, 2),
                sector=stock.sector if stock else None,
            ))

        return PortfolioResponse(
            id=portfolio.id, total_value=portfolio.total_value,
            cash_available=portfolio.cash_available, holdings=holdings,
        )

    async def get_summary(self, user_id: int) -> PortfolioSummary:
        result = await self.db.execute(
            select(Portfolio).options(selectinload(Portfolio.holdings)).where(Portfolio.user_id == user_id)
        )
        portfolio = result.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

        sectors = set()
        for h in portfolio.holdings:
            stock = await self._get_stock(h.stock_id)
            if stock and stock.sector:
                sectors.add(stock.sector)

        cash_pct = (portfolio.cash_available / portfolio.total_value * 100) if portfolio.total_value > 0 else 100

        return PortfolioSummary(
            total_value=portfolio.total_value,
            cash_available=portfolio.cash_available,
            holdings_count=len(portfolio.holdings),
            sectors_count=len(sectors),
            cash_percent=round(cash_pct, 1),
        )

    async def execute_trade(self, user_id: int, order: OrderCreate) -> OrderResponse:
        result = await self.db.execute(
            select(Portfolio).options(selectinload(Portfolio.holdings)).where(Portfolio.user_id == user_id)
        )
        portfolio = result.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

        # Resolve stock
        stock_result = await self.db.execute(select(Stock).where(Stock.ticker == order.ticker.upper()))
        stock = stock_result.scalar_one_or_none()
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock {order.ticker} not found")

        price = order.limit_price if order.limit_price else await self._get_current_price(stock.id)
        if price == 0:
            price = 150.0  # fallback mock price for paper trading

        total_value = order.quantity * price

        if order.order_type == "buy":
            if total_value > portfolio.cash_available:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient cash available")
            portfolio.cash_available -= total_value
            await self._add_to_holdings(portfolio, stock.id, order.quantity, price)
        else:
            holding = next((h for h in portfolio.holdings if h.stock_id == stock.id), None)
            if not holding or holding.quantity < order.quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient shares")
            holding.quantity -= order.quantity
            if holding.quantity <= 0:
                await self.db.delete(holding)
            portfolio.cash_available += total_value

        self._recalculate_portfolio(portfolio)

        trade = Trade(
            portfolio_id=portfolio.id, stock_id=stock.id, order_type=order.order_type,
            quantity=order.quantity, price_executed=price, total_value=total_value,
            order_ticket_details=order.order_ticket_details,
        )
        self.db.add(trade)
        await self.db.flush()

        return OrderResponse(
            id=trade.id, stock_id=trade.stock_id, order_type=trade.order_type,
            quantity=trade.quantity, price_executed=trade.price_executed,
            total_value=trade.total_value, executed_at=trade.executed_at,
        )

    async def get_trade_history(self, user_id: int, limit: int = 50) -> list[TradeHistoryItem]:
        result = await self.db.execute(select(Portfolio).where(Portfolio.user_id == user_id))
        portfolio = result.scalar_one_or_none()
        if not portfolio:
            return []

        trades_result = await self.db.execute(
            select(Trade).where(Trade.portfolio_id == portfolio.id).order_by(Trade.executed_at.desc()).limit(limit)
        )
        trades = trades_result.scalars().all()

        items = []
        for t in trades:
            stock = await self._get_stock(t.stock_id)
            items.append(TradeHistoryItem(
                id=t.id, ticker=stock.ticker if stock else "???",
                order_type=t.order_type, quantity=t.quantity,
                price_executed=t.price_executed, total_value=t.total_value,
                executed_at=t.executed_at,
            ))
        return items

    async def _get_stock(self, stock_id: int) -> Stock | None:
        result = await self.db.execute(select(Stock).where(Stock.id == stock_id))
        return result.scalar_one_or_none()

    async def _get_current_price(self, stock_id: int) -> float:
        result = await self.db.execute(
            select(StockPrice).where(StockPrice.stock_id == stock_id).order_by(StockPrice.time.desc()).limit(1)
        )
        price = result.scalar_one_or_none()
        return price.close if price and price.close else 0.0

    async def _add_to_holdings(self, portfolio: Portfolio, stock_id: int, quantity: float, price: float):
        existing = next((h for h in portfolio.holdings if h.stock_id == stock_id), None)
        if existing:
            total_qty = existing.quantity + quantity
            existing.average_buy_price = ((existing.average_buy_price * existing.quantity) + (price * quantity)) / total_qty
            existing.quantity = total_qty
        else:
            holding = Holding(
                portfolio_id=portfolio.id, stock_id=stock_id,
                quantity=quantity, average_buy_price=price,
            )
            self.db.add(holding)

    def _recalculate_portfolio(self, portfolio: Portfolio):
        holdings_value = sum(h.quantity * h.average_buy_price for h in portfolio.holdings if h.quantity > 0)
        portfolio.total_value = portfolio.cash_available + holdings_value
