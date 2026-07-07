from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.flags import RiskFlag
from app.models.stock import Stock
from app.models.portfolio import Portfolio, Holding
from app.schemas.flags import RiskFlagResponse, CompositeScoreResponse, PortfolioRiskSummary
from app.core.constants import RISK_THRESHOLDS


class FlagService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_flags_for_ticker(self, ticker: str) -> list[RiskFlagResponse]:
        stock = await self._get_stock_by_ticker(ticker)
        if not stock:
            return []

        result = await self.db.execute(
            select(RiskFlag)
            .where(RiskFlag.stock_id == stock.id)
            .order_by(RiskFlag.severity_score.desc())
        )
        flags = result.scalars().all()
        return [RiskFlagResponse.model_validate(f) for f in flags]

    async def get_composite_score(self, ticker: str) -> CompositeScoreResponse:
        stock = await self._get_stock_by_ticker(ticker)
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Stock {ticker} not found")

        result = await self.db.execute(
            select(RiskFlag).where(RiskFlag.stock_id == stock.id).order_by(RiskFlag.calculated_at.desc())
        )
        flags = result.scalars().all()

        if not flags:
            return CompositeScoreResponse(
                stock_id=stock.id, ticker=ticker, overall_score=0,
                severity="low", flags=[],
            )

        overall = int(sum(f.severity_score or 0 for f in flags) / len(flags)) if flags else 0
        severity = self._score_to_severity(overall)

        return CompositeScoreResponse(
            stock_id=stock.id, ticker=ticker, overall_score=overall,
            severity=severity,
            flags=[RiskFlagResponse.model_validate(f) for f in flags[:10]],
        )

    async def get_portfolio_risk_summary(self, user_id: int) -> PortfolioRiskSummary:
        result = await self.db.execute(select(Portfolio).where(Portfolio.user_id == user_id))
        portfolio = result.scalar_one_or_none()
        if not portfolio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

        holdings_result = await self.db.execute(
            select(Holding).where(Holding.portfolio_id == portfolio.id)
        )
        holdings = holdings_result.scalars().all()

        if not holdings:
            return PortfolioRiskSummary(
                composite_risk=0, severity="low",
                concentration_warnings=[], diversification_score=100.0,
                explanation="No holdings yet. Your portfolio is all cash.",
            )

        # Calculate per-holding risk
        scores = []
        sector_values: dict[str, float] = {}
        total_invested = 0.0

        for h in holdings:
            value = h.quantity * h.average_buy_price
            total_invested += value
            stock = await self._get_stock_by_id(h.stock_id)
            sector = stock.sector if stock else "Unknown"
            sector_values[sector] = sector_values.get(sector, 0) + value

            flag_result = await self.db.execute(
                select(RiskFlag).where(RiskFlag.stock_id == h.stock_id)
            )
            flags = flag_result.scalars().all()
            if flags:
                avg_score = sum(f.severity_score or 0 for f in flags) / len(flags)
                weight = value / total_invested if total_invested > 0 else 0
                scores.append(avg_score * weight)

        composite = int(sum(scores)) if scores else 0
        severity = self._score_to_severity(composite)

        # Concentration warnings
        warnings = []
        for sector, val in sector_values.items():
            pct = (val / total_invested * 100) if total_invested > 0 else 0
            if pct > 50:
                warnings.append(f"Concentrated in {sector} ({pct:.0f}%) — consider diversifying")

        diversification = max(0, 100 - (max(sector_values.values()) / total_invested * 100)) if total_invested > 0 else 100

        return PortfolioRiskSummary(
            composite_risk=composite, severity=severity,
            concentration_warnings=warnings,
            diversification_score=round(diversification, 1),
            explanation=f"Portfolio risk score: {composite}/100 ({severity}). {len(holdings)} holdings across {len(sector_values)} sectors.",
        )

    async def _get_stock_by_ticker(self, ticker: str) -> Stock | None:
        result = await self.db.execute(select(Stock).where(Stock.ticker == ticker))
        return result.scalar_one_or_none()

    async def _get_stock_by_id(self, stock_id: int) -> Stock | None:
        result = await self.db.execute(select(Stock).where(Stock.id == stock_id))
        return result.scalar_one_or_none()

    @staticmethod
    def _score_to_severity(score: int) -> str:
        for sev, (low, high) in RISK_THRESHOLDS.items():
            if low <= score <= high:
                return sev
        return "low"
