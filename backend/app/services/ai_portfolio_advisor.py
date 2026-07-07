"""
AI Portfolio Advisor — Weekly analysis of portfolio health.

Features:
- Diversification scoring
- Concentration risk detection
- Missing sector identification
- Rebalancing suggestions
- Position sizing alerts
- Correlation analysis
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from collections import Counter

from app.models.portfolio import Portfolio, Holding, Trade
from app.models.company import Company
from app.models.sector import Sector
from app.models.ai import AIPortfolioAdvice
from app.models.flags import RiskFlag


class AIPortfolioAdvisor:
    IDEAL_MAX_POSITION_PCT = 25.0
    IDEAL_MIN_POSITIONS = 5
    IDEAL_SECTOR_COUNT = 4

    def __init__(self, db: Session):
        self.db = db

    def generate_advice(
        self,
        user_id: int,
        portfolio_id: Optional[int] = None,
        advice_type: str = "weekly_review"
    ) -> AIPortfolioAdvice:
        portfolio = self._get_portfolio(user_id, portfolio_id)
        holdings = self._get_holdings(portfolio.id)

        if not holdings:
            return self._empty_advice(user_id, portfolio.id, advice_type)

        analysis = self._analyze_portfolio(portfolio, holdings)

        advice = AIPortfolioAdvice(
            user_id=user_id,
            portfolio_id=portfolio.id,
            advice_type=advice_type,
            overall_health_score=analysis["overall_health_score"],
            diversification_score=analysis["diversification_score"],
            concentration_risk=analysis["concentration_risk"],
            missing_sectors=analysis["missing_sectors"],
            suggestions=analysis["suggestions"],
            portfolio_snapshot=analysis["snapshot"],
            model_used="prestocks-advisor-v1"
        )

        self.db.add(advice)
        self.db.commit()
        self.db.refresh(advice)
        return advice

    def _get_portfolio(self, user_id: int, portfolio_id: Optional[int]) -> Portfolio:
        if portfolio_id:
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.id == portfolio_id, Portfolio.user_id == user_id
            ).first()
        else:
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.user_id == user_id, Portfolio.is_default == True
            ).first()

        if not portfolio:
            raise ValueError("Portfolio not found")
        return portfolio

    def _get_holdings(self, portfolio_id: int) -> List[Holding]:
        return self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()

    def _analyze_portfolio(self, portfolio: Portfolio, holdings: List[Holding]) -> dict:
        total_invested = sum(h.quantity * h.average_buy_price for h in holdings)
        total_value = portfolio.total_value or (total_invested + portfolio.cash_available)

        positions = []
        sector_allocation = Counter()
        risk_scores = []

        for h in holdings:
            company = self.db.query(Company).filter(Company.id == h.company_id).first()
            if not company:
                continue

            position_value = h.quantity * h.average_buy_price
            weight = (position_value / total_value * 100) if total_value > 0 else 0

            sector_name = "Unknown"
            if company.sector_id:
                sector = self.db.query(Sector).filter(Sector.id == company.sector_id).first()
                if sector:
                    sector_name = sector.name

            sector_allocation[sector_name] += weight

            flags = self.db.query(RiskFlag).filter(
                RiskFlag.company_id == company.id, RiskFlag.is_active == True
            ).all()
            avg_risk = sum(f.severity_score for f in flags) / len(flags) if flags else 30

            positions.append({
                "company_id": company.id,
                "ticker": company.ticker,
                "name": company.name,
                "sector": sector_name,
                "weight_pct": round(weight, 2),
                "value": round(position_value, 2),
                "risk_score": round(avg_risk, 1)
            })
            risk_scores.append(avg_risk)

        concentration_risk = self._assess_concentration(positions)
        diversification_score = self._score_diversification(positions, sector_allocation)
        missing_sectors = self._find_missing_sectors(sector_allocation)
        suggestions = self._generate_suggestions(
            positions, sector_allocation, concentration_risk, missing_sectors, portfolio
        )

        overall_health = self._calculate_overall_health(
            diversification_score, concentration_risk, risk_scores, portfolio
        )

        snapshot = {
            "total_value": round(total_value, 2),
            "cash_available": round(portfolio.cash_available, 2),
            "cash_pct": round((portfolio.cash_available / total_value * 100) if total_value > 0 else 100, 1),
            "num_positions": len(positions),
            "positions": positions,
            "sector_allocation": dict(sector_allocation),
            "avg_risk_score": round(sum(risk_scores) / len(risk_scores), 1) if risk_scores else 0
        }

        return {
            "overall_health_score": overall_health,
            "diversification_score": diversification_score,
            "concentration_risk": concentration_risk,
            "missing_sectors": missing_sectors,
            "suggestions": suggestions,
            "snapshot": snapshot
        }

    def _assess_concentration(self, positions: list) -> dict:
        if not positions:
            return {"level": "none", "details": []}

        sorted_pos = sorted(positions, key=lambda x: x["weight_pct"], reverse=True)
        top_position = sorted_pos[0]

        issues = []
        level = "low"

        if top_position["weight_pct"] > 40:
            level = "critical"
            issues.append({
                "type": "single_position",
                "ticker": top_position["ticker"],
                "weight": top_position["weight_pct"],
                "message": f"{top_position['ticker']} is {top_position['weight_pct']:.1f}% of your portfolio. This is extremely concentrated."
            })
        elif top_position["weight_pct"] > self.IDEAL_MAX_POSITION_PCT:
            level = "high"
            issues.append({
                "type": "single_position",
                "ticker": top_position["ticker"],
                "weight": top_position["weight_pct"],
                "message": f"{top_position['ticker']} at {top_position['weight_pct']:.1f}% exceeds recommended 25% max per position."
            })

        top_3_weight = sum(p["weight_pct"] for p in sorted_pos[:3])
        if top_3_weight > 80 and len(positions) > 3:
            level = max(level, "high")
            issues.append({
                "type": "top_heavy",
                "weight": top_3_weight,
                "message": f"Top 3 positions represent {top_3_weight:.1f}% of portfolio. Consider distributing more evenly."
            })

        return {"level": level, "details": issues}

    def _score_diversification(self, positions: list, sector_allocation: Counter) -> int:
        if not positions:
            return 0

        score = 50

        num_positions = len(positions)
        if num_positions >= 10: score += 20
        elif num_positions >= 7: score += 15
        elif num_positions >= 5: score += 10
        elif num_positions >= 3: score += 5
        else: score -= 10

        num_sectors = len(sector_allocation)
        if num_sectors >= 6: score += 20
        elif num_sectors >= 4: score += 15
        elif num_sectors >= 3: score += 10
        elif num_sectors >= 2: score += 5
        else: score -= 15

        weights = [p["weight_pct"] for p in positions]
        max_weight = max(weights)
        if max_weight <= 15: score += 10
        elif max_weight <= 25: score += 5
        elif max_weight > 40: score -= 15

        return max(0, min(100, score))

    def _find_missing_sectors(self, sector_allocation: Counter) -> list:
        core_sectors = [
            "Technology", "Healthcare", "Financial Services",
            "Consumer Discretionary", "Energy", "Industrials",
            "Real Estate", "Materials", "Utilities"
        ]

        present = set(sector_allocation.keys())
        missing = [s for s in core_sectors if s not in present]

        recommendations = []
        for sector in missing[:5]:
            recommendations.append({
                "sector": sector,
                "reason": f"Adding {sector} exposure would improve diversification",
                "priority": "high" if sector in ["Technology", "Healthcare", "Financial Services"] else "medium"
            })

        return recommendations

    def _generate_suggestions(self, positions, sector_allocation, concentration_risk, missing_sectors, portfolio) -> list:
        suggestions = []

        if concentration_risk["level"] in ("high", "critical"):
            for issue in concentration_risk["details"][:2]:
                if issue["type"] == "single_position":
                    suggestions.append({
                        "type": "rebalance",
                        "priority": "high",
                        "action": f"Consider reducing {issue['ticker']} position from {issue['weight']:.1f}% to under 25%",
                        "reasoning": "Single-stock concentration creates unnecessary idiosyncratic risk"
                    })

        if missing_sectors and len(sector_allocation) < self.IDEAL_SECTOR_COUNT:
            top_missing = missing_sectors[0]
            suggestions.append({
                "type": "diversify",
                "priority": "medium",
                "action": f"Consider adding {top_missing['sector']} exposure to your portfolio",
                "reasoning": "Sector diversification reduces correlation risk during market stress"
            })

        cash_pct = (portfolio.cash_available / portfolio.total_value * 100) if portfolio.total_value > 0 else 100
        if cash_pct > 50:
            suggestions.append({
                "type": "deploy_capital",
                "priority": "medium",
                "action": f"You have {cash_pct:.0f}% in cash. Consider deploying into diversified positions",
                "reasoning": "Excess cash underperforms inflation long-term"
            })
        elif cash_pct < 5:
            suggestions.append({
                "type": "build_reserve",
                "priority": "low",
                "action": "Consider maintaining at least 5-10% cash reserve for opportunities",
                "reasoning": "Cash reserves allow buying during market dips"
            })

        high_risk_positions = [p for p in positions if p["risk_score"] > 70]
        if high_risk_positions:
            total_high_risk_weight = sum(p["weight_pct"] for p in high_risk_positions)
            if total_high_risk_weight > 30:
                suggestions.append({
                    "type": "risk_reduction",
                    "priority": "high",
                    "action": f"High-risk positions ({total_high_risk_weight:.0f}% of portfolio) exceed recommended 30% threshold",
                    "reasoning": "Reduce exposure to high-risk flags to protect capital"
                })

        if not suggestions:
            suggestions.append({
                "type": "maintain",
                "priority": "low",
                "action": "Portfolio looks well-balanced. Continue monitoring and learning.",
                "reasoning": "No immediate action needed"
            })

        return suggestions

    def _calculate_overall_health(self, diversification_score, concentration_risk, risk_scores, portfolio) -> int:
        score = diversification_score * 0.4

        conc_penalty = {"low": 0, "high": -15, "critical": -30, "none": 0}
        score += 30 + conc_penalty.get(concentration_risk["level"], 0)

        if risk_scores:
            avg_risk = sum(risk_scores) / len(risk_scores)
            risk_health = max(0, 100 - avg_risk)
            score += risk_health * 0.2

        cash_pct = (portfolio.cash_available / portfolio.total_value * 100) if portfolio.total_value > 0 else 100
        if 5 <= cash_pct <= 30:
            score += 10
        elif cash_pct > 80:
            score -= 5

        return max(0, min(100, int(score)))

    def _empty_advice(self, user_id: int, portfolio_id: int, advice_type: str) -> AIPortfolioAdvice:
        advice = AIPortfolioAdvice(
            user_id=user_id,
            portfolio_id=portfolio_id,
            advice_type=advice_type,
            overall_health_score=50,
            diversification_score=0,
            concentration_risk={"level": "none", "details": []},
            missing_sectors=[{"sector": "Any", "reason": "Portfolio is empty. Start by researching companies.", "priority": "high"}],
            suggestions=[{
                "type": "start",
                "priority": "high",
                "action": "Begin by adding companies to your watchlist, then make your first paper trade",
                "reasoning": "Building a diversified portfolio starts with research"
            }],
            portfolio_snapshot={"total_value": 10000, "cash_available": 10000, "num_positions": 0},
            model_used="prestocks-advisor-v1"
        )
        self.db.add(advice)
        self.db.commit()
        self.db.refresh(advice)
        return advice
