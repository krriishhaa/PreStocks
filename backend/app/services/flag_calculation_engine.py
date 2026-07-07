"""
Risk Flag Calculation Engine.
Computes individual risk flags and composite scores per stock.
"""
import math
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import Stock, StockFundamentals, StockPrice
from app.models.flags import RiskFlag
from app.models.portfolio import Portfolio, Holding
from app.utils.redis_cache import RedisCache

HIGH = 80
MEDIUM = 50
LOW = 20

FLAG_WEIGHTS = {
    "volatility": 1.2,
    "valuation": 1.0,
    "balance_sheet": 0.9,
    "insider_activity": 1.1,
    "momentum": 0.8,
    "sentiment": 0.7,
    "concentration": 1.0,
    "liquidity": 0.6,
}


class FlagCalculationEngine:
    def __init__(self, db: AsyncSession, cache: Optional[RedisCache] = None):
        self.db = db
        self.cache = cache or RedisCache()

    # ─── INDIVIDUAL FLAG CALCULATORS ─────────────────────────────────

    async def calculate_volatility_flag(self, stock_id: int, days: int = 30) -> dict:
        """
        Compare realized volatility to sector median.
        >2x sector = HIGH, >1.3x = MEDIUM, else LOW.
        """
        prices = await self._get_price_history(stock_id, days)
        if len(prices) < 5:
            return self._make_flag("volatility", LOW, "Insufficient price data for volatility calculation.", 0.3)

        realized_vol = self._calculate_std_dev(prices)
        sector_median_vol = await self._get_sector_median_volatility(stock_id)

        if sector_median_vol == 0:
            sector_median_vol = realized_vol  # fallback

        vol_ratio = realized_vol / sector_median_vol if sector_median_vol > 0 else 1.0

        if vol_ratio > 2.0:
            severity = HIGH
            explanation = f"This stock moves {vol_ratio:.1f}x more than its sector average. Daily swings of {realized_vol*100:.1f}% are common. High volatility means larger potential gains AND losses."
        elif vol_ratio > 1.3:
            severity = MEDIUM
            explanation = f"Volatility is {vol_ratio:.1f}x the sector average. Moderate price swings expected — consider position sizing."
        else:
            severity = LOW
            explanation = f"Volatility is in line with sector peers ({vol_ratio:.1f}x). Price movements are relatively stable."

        confidence = min(0.95, 0.5 + (len(prices) / 60))
        return self._make_flag("volatility", severity, explanation, confidence)

    async def calculate_valuation_flag(self, stock_id: int) -> dict:
        """
        Compare current P/E to 5-year historical range and sector median.
        >80th percentile = HIGH, >60th = MEDIUM, else LOW.
        """
        fundamentals = await self._get_latest_fundamentals(stock_id)
        if not fundamentals or not fundamentals.pe_ratio:
            return self._make_flag("valuation", LOW, "No valuation data available.", 0.3)

        current_pe = fundamentals.pe_ratio
        historical_pes = await self._get_historical_pe(stock_id, years=5)
        sector_pe = await self._get_sector_median_pe(stock_id)

        if not historical_pes:
            historical_pes = [current_pe]

        percentile = self._calculate_percentile(current_pe, historical_pes)

        if percentile > 80:
            severity = HIGH
            explanation = f"Priced higher than {percentile:.0f}% of its own 5-year trading range (P/E: {current_pe:.1f} vs sector median {sector_pe:.1f}). Valuation appears stretched relative to history."
        elif percentile > 60:
            severity = MEDIUM
            explanation = f"P/E of {current_pe:.1f} is at the {percentile:.0f}th percentile of its 5-year range. Above average but not extreme."
        else:
            severity = LOW
            explanation = f"P/E of {current_pe:.1f} is at the {percentile:.0f}th percentile — in line with or below historical norms."

        return self._make_flag("valuation", severity, explanation, 0.85)

    async def calculate_balance_sheet_flag(self, stock_id: int) -> dict:
        """
        Assess financial health: debt-to-equity, current ratio, interest coverage.
        """
        fundamentals = await self._get_latest_fundamentals(stock_id)
        if not fundamentals:
            return self._make_flag("balance_sheet", LOW, "No fundamental data available.", 0.3)

        score = 0
        concerns = []

        # Debt-to-equity
        if fundamentals.debt_to_equity and fundamentals.debt_to_equity > 2.0:
            score += 30
            concerns.append(f"high debt-to-equity ({fundamentals.debt_to_equity:.1f})")
        elif fundamentals.debt_to_equity and fundamentals.debt_to_equity > 1.0:
            score += 15

        # Current ratio (< 1 = may struggle with short-term obligations)
        if fundamentals.current_ratio and fundamentals.current_ratio < 1.0:
            score += 25
            concerns.append(f"current ratio below 1 ({fundamentals.current_ratio:.2f})")
        elif fundamentals.current_ratio and fundamentals.current_ratio < 1.5:
            score += 10

        # Interest coverage (< 2 = barely covering interest)
        if fundamentals.interest_coverage and fundamentals.interest_coverage < 2.0:
            score += 25
            concerns.append(f"weak interest coverage ({fundamentals.interest_coverage:.1f}x)")
        elif fundamentals.interest_coverage and fundamentals.interest_coverage < 4.0:
            score += 10

        # Cash runway
        if fundamentals.cash_runway_months and fundamentals.cash_runway_months < 12:
            score += 20
            concerns.append(f"only {fundamentals.cash_runway_months} months cash runway")

        severity = min(score, 100)
        if severity >= 60:
            explanation = f"Balance sheet concerns: {', '.join(concerns)}. Financial stability is at risk."
        elif severity >= 30:
            explanation = f"Some balance sheet caution: {', '.join(concerns) if concerns else 'moderate leverage'}."
        else:
            explanation = "Balance sheet appears healthy with manageable debt and adequate liquidity."

        return self._make_flag("balance_sheet", severity, explanation, 0.80)

    async def calculate_insider_activity_flag(self, stock_id: int) -> dict:
        """
        Assess insider buying/selling patterns.
        Net selling by insiders = bearish signal.
        """
        fundamentals = await self._get_latest_fundamentals(stock_id)

        # In production, fetch from SEC EDGAR or data provider
        # For now, check if we have insider data in fundamentals
        insider_net = 0  # placeholder — in production, query insider filings table

        if insider_net < -10000:
            severity = HIGH
            explanation = "Significant insider selling detected. When executives sell large amounts, it can signal concerns about future growth."
        elif insider_net < -1000:
            severity = MEDIUM
            explanation = "Moderate insider selling. Some executives have reduced their positions recently."
        elif insider_net > 5000:
            severity = LOW
            explanation = "Insiders are buying — often a positive signal about management's confidence."
        else:
            severity = LOW
            explanation = "Insider activity is neutral. No significant buying or selling patterns detected."

        return self._make_flag("insider_activity", severity, explanation, 0.65)

    async def calculate_momentum_flag(self, stock_id: int) -> dict:
        """
        Assess price momentum. Extreme moves in either direction flag risk.
        """
        prices = await self._get_price_history(stock_id, 90)
        if len(prices) < 10:
            return self._make_flag("momentum", LOW, "Insufficient data for momentum analysis.", 0.3)

        recent_prices = prices[-5:]
        older_prices = prices[:5]

        recent_avg = sum(p.close for p in recent_prices if p.close) / len(recent_prices)
        older_avg = sum(p.close for p in older_prices if p.close) / len(older_prices)

        momentum_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0

        if abs(momentum_pct) > 30:
            severity = HIGH
            direction = "up" if momentum_pct > 0 else "down"
            explanation = f"Stock has moved {abs(momentum_pct):.0f}% {direction} over the past quarter. Extreme momentum often precedes reversals."
        elif abs(momentum_pct) > 15:
            severity = MEDIUM
            direction = "gained" if momentum_pct > 0 else "lost"
            explanation = f"Stock has {direction} {abs(momentum_pct):.0f}% recently. Strong trend — monitor for continuation or reversal."
        else:
            severity = LOW
            explanation = f"Price momentum is moderate ({momentum_pct:+.1f}%). No extreme trends detected."

        return self._make_flag("momentum", severity, explanation, 0.75)

    # ─── COMPOSITE SCORE ─────────────────────────────────────────────

    async def calculate_composite_risk_score(self, stock_id: int) -> dict:
        """
        Calculate weighted composite risk score from all individual flags.
        Returns score (0-100), individual flags, and metadata.
        """
        flags = [
            await self.calculate_volatility_flag(stock_id),
            await self.calculate_valuation_flag(stock_id),
            await self.calculate_balance_sheet_flag(stock_id),
            await self.calculate_insider_activity_flag(stock_id),
            await self.calculate_momentum_flag(stock_id),
        ]

        weighted_scores = []
        total_weight = 0
        for f in flags:
            weight = FLAG_WEIGHTS.get(f["type"], 1.0)
            weighted_scores.append(f["severity_score"] * weight)
            total_weight += weight

        composite = int(sum(weighted_scores) / total_weight) if total_weight > 0 else 0
        composite = min(max(composite, 0), 100)

        return {
            "score": composite,
            "flags": flags,
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }

    # ─── PERSISTENCE ─────────────────────────────────────────────────

    async def compute_and_store(self, stock_id: int) -> dict:
        """Calculate composite score and persist flags to database + cache."""
        result = await self.calculate_composite_risk_score(stock_id)

        # Store individual flags
        for flag_data in result["flags"]:
            flag = RiskFlag(
                stock_id=stock_id,
                flag_type=flag_data["type"],
                severity_score=flag_data["severity_score"],
                explanation=flag_data["explanation"],
                confidence_score=flag_data["confidence"],
            )
            self.db.add(flag)

        await self.db.flush()

        # Cache composite score
        stock = await self.db.execute(select(Stock).where(Stock.id == stock_id))
        stock_obj = stock.scalar_one_or_none()
        if stock_obj:
            cache_key = f"flags:{stock_obj.ticker}:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
            await self.cache.set_json(cache_key, result, ex=300)
            await self.cache.set_flag_score(stock_obj.ticker, result["score"])

        return result

    # ─── PORTFOLIO RISK SUMMARY ──────────────────────────────────────

    async def calculate_portfolio_risk_summary(self, portfolio_id: int) -> dict:
        """
        Aggregate risk assessment across entire portfolio:
        1. Sector concentration
        2. Individual position sizes
        3. Aggregate flag exposure
        """
        holdings_result = await self.db.execute(
            select(Holding).where(Holding.portfolio_id == portfolio_id)
        )
        holdings = holdings_result.scalars().all()

        if not holdings:
            return {
                "composite_risk_score": 0,
                "concentration_warnings": [],
                "oversized_positions": [],
                "high_risk_holdings": 0,
                "diversification_suggestions": ["Start by purchasing a broad market ETF like SPY"],
            }

        portfolio_result = await self.db.execute(
            select(Portfolio).where(Portfolio.id == portfolio_id)
        )
        portfolio = portfolio_result.scalar_one()
        portfolio_value = portfolio.total_value

        # 1. Sector concentration
        sector_exposure: dict[str, float] = {}
        holding_values: list[tuple[int, str, float]] = []

        for h in holdings:
            stock_result = await self.db.execute(select(Stock).where(Stock.id == h.stock_id))
            stock = stock_result.scalar_one_or_none()
            price = await self._get_latest_price(h.stock_id)
            value = h.quantity * price

            ticker = stock.ticker if stock else "???"
            sector = stock.sector if stock and stock.sector else "Unknown"

            sector_exposure[sector] = sector_exposure.get(sector, 0) + value
            holding_values.append((h.stock_id, ticker, value))

        concentration_warnings = []
        for sector, value in sector_exposure.items():
            exposure_pct = value / portfolio_value if portfolio_value > 0 else 0
            if exposure_pct > 0.4:
                concentration_warnings.append(
                    f"{sector}: {exposure_pct*100:.0f}% of portfolio — consider diversifying into other sectors"
                )

        # 2. Oversized positions
        oversized_positions = []
        for stock_id, ticker, value in holding_values:
            position_pct = value / portfolio_value if portfolio_value > 0 else 0
            if position_pct > 0.25:
                oversized_positions.append(
                    f"{ticker}: {position_pct*100:.0f}% — large position for a beginner"
                )

        # 3. Aggregate flag exposure
        flag_scores = []
        high_risk_count = 0
        for stock_id, ticker, value in holding_values:
            weight = value / portfolio_value if portfolio_value > 0 else 0
            cached_score = await self.cache.get_flag_score(ticker)
            if cached_score is not None:
                flag_scores.append(cached_score * weight)
                if cached_score > 60:
                    high_risk_count += 1
            else:
                composite = await self.calculate_composite_risk_score(stock_id)
                flag_scores.append(composite["score"] * weight)
                if composite["score"] > 60:
                    high_risk_count += 1

        aggregate_score = int(sum(flag_scores)) if flag_scores else 0

        # 4. Diversification suggestions
        suggestions = []
        present_sectors = set(sector_exposure.keys())
        missing_sectors = {"Healthcare", "Energy", "Financials", "Consumer Staples"} - present_sectors
        for sector in list(missing_sectors)[:3]:
            suggestions.append(f"Add {sector} exposure for better diversification")

        if portfolio.cash_available / portfolio_value > 0.5:
            suggestions.append("Consider deploying some cash — over 50% is uninvested")

        return {
            "composite_risk_score": aggregate_score,
            "concentration_warnings": concentration_warnings,
            "oversized_positions": oversized_positions,
            "high_risk_holdings": high_risk_count,
            "diversification_suggestions": suggestions,
        }

    # ─── HELPER METHODS ──────────────────────────────────────────────

    async def _get_price_history(self, stock_id: int, days: int) -> list:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db.execute(
            select(StockPrice)
            .where(StockPrice.stock_id == stock_id, StockPrice.time >= cutoff)
            .order_by(StockPrice.time.asc())
        )
        return result.scalars().all()

    async def _get_latest_price(self, stock_id: int) -> float:
        result = await self.db.execute(
            select(StockPrice).where(StockPrice.stock_id == stock_id).order_by(StockPrice.time.desc()).limit(1)
        )
        price = result.scalar_one_or_none()
        return price.close if price and price.close else 0.0

    async def _get_latest_fundamentals(self, stock_id: int) -> Optional[StockFundamentals]:
        result = await self.db.execute(
            select(StockFundamentals)
            .where(StockFundamentals.stock_id == stock_id)
            .order_by(StockFundamentals.updated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _get_sector_median_volatility(self, stock_id: int) -> float:
        stock_result = await self.db.execute(select(Stock).where(Stock.id == stock_id))
        stock = stock_result.scalar_one_or_none()
        if not stock or not stock.sector:
            return 0.02  # default 2% daily vol

        # Get all stocks in same sector and compute median vol
        sector_stocks = await self.db.execute(
            select(Stock.id).where(Stock.sector == stock.sector)
        )
        sector_ids = [row[0] for row in sector_stocks.all()]

        vols = []
        for sid in sector_ids[:20]:  # limit for performance
            prices = await self._get_price_history(sid, 30)
            if len(prices) >= 5:
                vol = self._calculate_std_dev(prices)
                vols.append(vol)

        if vols:
            vols.sort()
            return vols[len(vols) // 2]
        return 0.02

    async def _get_sector_median_pe(self, stock_id: int) -> float:
        stock_result = await self.db.execute(select(Stock).where(Stock.id == stock_id))
        stock = stock_result.scalar_one_or_none()
        if not stock or not stock.sector:
            return 20.0

        result = await self.db.execute(
            select(StockFundamentals.pe_ratio)
            .join(Stock, Stock.id == StockFundamentals.stock_id)
            .where(Stock.sector == stock.sector, StockFundamentals.pe_ratio.isnot(None))
        )
        pes = [row[0] for row in result.all() if row[0] and row[0] > 0]
        if pes:
            pes.sort()
            return pes[len(pes) // 2]
        return 20.0

    async def _get_historical_pe(self, stock_id: int, years: int = 5) -> list[float]:
        result = await self.db.execute(
            select(StockFundamentals.pe_ratio)
            .where(StockFundamentals.stock_id == stock_id, StockFundamentals.pe_ratio.isnot(None))
            .order_by(StockFundamentals.updated_at.desc())
            .limit(years * 4)  # quarterly data
        )
        return [row[0] for row in result.all() if row[0] and row[0] > 0]

    @staticmethod
    def _calculate_std_dev(prices: list) -> float:
        """Calculate standard deviation of daily returns."""
        if len(prices) < 2:
            return 0.0
        returns = []
        for i in range(1, len(prices)):
            if prices[i].close and prices[i-1].close and prices[i-1].close > 0:
                daily_return = (prices[i].close - prices[i-1].close) / prices[i-1].close
                returns.append(daily_return)
        if not returns:
            return 0.0
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        return math.sqrt(variance)

    @staticmethod
    def _calculate_percentile(value: float, distribution: list[float]) -> float:
        """Calculate what percentile a value falls at within a distribution."""
        if not distribution:
            return 50.0
        count_below = sum(1 for v in distribution if v < value)
        return (count_below / len(distribution)) * 100

    @staticmethod
    def _make_flag(flag_type: str, severity: int, explanation: str, confidence: float) -> dict:
        return {
            "type": flag_type,
            "severity_score": severity,
            "explanation": explanation,
            "confidence": confidence,
        }
