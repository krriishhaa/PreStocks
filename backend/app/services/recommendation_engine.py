"""
Recommendation Engine — Suggests companies, sectors, and watchlists.

Generates personalized suggestions based on:
- User's current portfolio composition
- Risk tier and investment preferences
- Sector gaps and diversification needs
- Trending companies and momentum
- Risk-adjusted opportunity scoring
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from collections import Counter

from app.models.user import User
from app.models.portfolio import Portfolio, Holding, Watchlist, WatchlistItem
from app.models.company import Company, CompanyFundamentals
from app.models.sector import Sector
from app.models.flags import RiskFlag, CompositeRiskScore
from app.models.news import NewsArticle, NewsCompany


class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_recommendations(self, user_id: int) -> Dict:
        """Full recommendation suite for a user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        portfolio = self.db.query(Portfolio).filter(
            Portfolio.user_id == user_id, Portfolio.is_default == True
        ).first()

        holdings = []
        if portfolio:
            holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()

        return {
            "companies": self._recommend_companies(user, holdings),
            "sectors": self._recommend_sectors(user, holdings),
            "watchlists": self._recommend_watchlists(user, holdings),
            "generated_at": datetime.utcnow().isoformat(),
            "user_tier": user.risk_tier
        }

    def recommend_companies(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Recommend companies for the user to research."""
        user = self.db.query(User).filter(User.id == user_id).first()
        portfolio = self.db.query(Portfolio).filter(
            Portfolio.user_id == user_id, Portfolio.is_default == True
        ).first()
        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all() if portfolio else []
        return self._recommend_companies(user, holdings, limit)

    def recommend_sectors(self, user_id: int) -> List[Dict]:
        """Recommend sectors the user should explore."""
        user = self.db.query(User).filter(User.id == user_id).first()
        portfolio = self.db.query(Portfolio).filter(
            Portfolio.user_id == user_id, Portfolio.is_default == True
        ).first()
        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all() if portfolio else []
        return self._recommend_sectors(user, holdings)

    def recommend_watchlists(self, user_id: int) -> List[Dict]:
        """Suggest curated watchlists."""
        user = self.db.query(User).filter(User.id == user_id).first()
        portfolio = self.db.query(Portfolio).filter(
            Portfolio.user_id == user_id, Portfolio.is_default == True
        ).first()
        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all() if portfolio else []
        return self._recommend_watchlists(user, holdings)

    def _recommend_companies(self, user: User, holdings: List[Holding], limit: int = 10) -> List[Dict]:
        """Score and rank companies for recommendation."""
        held_company_ids = {h.company_id for h in holdings}

        candidates = (
            self.db.query(Company)
            .filter(Company.is_active == True, Company.id.notin_(held_company_ids) if held_company_ids else True)
            .limit(100)
            .all()
        )

        scored = []
        for company in candidates:
            score = self._score_company(company, user, holdings)
            if score["total"] > 0:
                scored.append({
                    "company_id": company.id,
                    "name": company.name,
                    "ticker": company.ticker,
                    "sector": company.industry or "Unknown",
                    "company_type": company.company_type,
                    "market_cap": company.market_cap,
                    "recommendation_score": score["total"],
                    "reasons": score["reasons"],
                    "risk_level": score["risk_level"],
                    "match_type": score["match_type"]
                })

        scored.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return scored[:limit]

    def _recommend_sectors(self, user: User, holdings: List[Holding]) -> List[Dict]:
        """Identify sectors the user should consider."""
        current_sectors = Counter()
        for h in holdings:
            company = self.db.query(Company).filter(Company.id == h.company_id).first()
            if company and company.sector_id:
                sector = self.db.query(Sector).filter(Sector.id == company.sector_id).first()
                if sector:
                    current_sectors[sector.name] += 1

        all_sectors = self.db.query(Sector).all()
        recommendations = []

        for sector in all_sectors:
            if sector.name not in current_sectors:
                company_count = self.db.query(Company).filter(
                    Company.sector_id == sector.id, Company.is_active == True
                ).count()

                if company_count == 0:
                    continue

                priority = "high" if sector.name in ["Technology", "Healthcare", "Financial Services"] else "medium"

                recommendations.append({
                    "sector_id": sector.id,
                    "name": sector.name,
                    "slug": sector.slug,
                    "available_companies": company_count,
                    "priority": priority,
                    "reason": f"You have no exposure to {sector.name}. Adding it would improve diversification.",
                    "risk_profile": self._sector_risk_profile(sector.id)
                })

        already_held = []
        for sector_name, count in current_sectors.items():
            sector = self.db.query(Sector).filter(Sector.name == sector_name).first()
            if sector:
                already_held.append({
                    "sector_id": sector.id,
                    "name": sector.name,
                    "current_holdings": count,
                    "status": "held",
                    "note": f"You already have {count} position(s) in {sector.name}."
                })

        return {
            "missing_sectors": sorted(recommendations, key=lambda x: x["priority"] == "high", reverse=True),
            "current_sectors": already_held,
            "diversification_tip": f"You're in {len(current_sectors)} sectors. Aim for 5-7 for good diversification."
        }

    def _recommend_watchlists(self, user: User, holdings: List[Holding]) -> List[Dict]:
        """Suggest curated watchlists based on user profile."""
        tier = user.risk_tier or "beginner"

        watchlists = []

        if tier == "beginner":
            watchlists.extend([
                {
                    "name": "Blue Chip Starters",
                    "description": "Large, stable companies ideal for learning. Lower volatility, strong brands.",
                    "criteria": {"min_market_cap": 100_000_000_000, "company_type": "public"},
                    "risk_level": "low",
                    "companies": self._get_watchlist_companies(min_cap=100e9, limit=8)
                },
                {
                    "name": "Dividend Growers",
                    "description": "Companies with consistent dividend growth. Great for understanding income investing.",
                    "criteria": {"has_dividend": True, "min_market_cap": 10_000_000_000},
                    "risk_level": "low",
                    "companies": self._get_watchlist_companies(min_cap=10e9, limit=6)
                },
            ])
        elif tier == "intermediate":
            watchlists.extend([
                {
                    "name": "Growth Leaders",
                    "description": "High-growth companies with strong momentum and market position.",
                    "criteria": {"min_revenue_growth": 20, "company_type": "public"},
                    "risk_level": "medium",
                    "companies": self._get_watchlist_companies(min_cap=10e9, limit=8)
                },
                {
                    "name": "Pre-IPO Watch",
                    "description": "Late-stage private companies approaching IPO. Higher risk, higher potential.",
                    "criteria": {"company_type": "pre_ipo"},
                    "risk_level": "high",
                    "companies": self._get_watchlist_companies(company_type="pre_ipo", limit=6)
                },
            ])
        else:
            watchlists.extend([
                {
                    "name": "High Conviction",
                    "description": "Concentrated bets on companies with strong competitive moats.",
                    "criteria": {"min_market_cap": 50_000_000_000},
                    "risk_level": "medium",
                    "companies": self._get_watchlist_companies(min_cap=50e9, limit=10)
                },
                {
                    "name": "Disruptors & Innovators",
                    "description": "Smaller companies challenging incumbents with new technology or business models.",
                    "criteria": {"max_market_cap": 50_000_000_000, "min_revenue_growth": 30},
                    "risk_level": "high",
                    "companies": self._get_watchlist_companies(max_cap=50e9, limit=8)
                },
            ])

        watchlists.append({
            "name": "Trending This Week",
            "description": "Most-discussed companies in the PreStocks community right now.",
            "criteria": {"trending": True},
            "risk_level": "varies",
            "companies": self._get_trending_companies(limit=6)
        })

        return watchlists

    def _score_company(self, company: Company, user: User, holdings: List[Holding]) -> Dict:
        """Score a company for recommendation relevance."""
        score = 0
        reasons = []
        risk_level = "medium"

        held_sectors = set()
        for h in holdings:
            c = self.db.query(Company).filter(Company.id == h.company_id).first()
            if c and c.sector_id:
                held_sectors.add(c.sector_id)

        if company.sector_id and company.sector_id not in held_sectors:
            score += 25
            reasons.append("Adds sector diversification")

        if company.market_cap:
            if company.market_cap > 100_000_000_000:
                if user.risk_tier == "beginner":
                    score += 20
                    reasons.append("Large-cap stability suits your tier")
                risk_level = "low"
            elif company.market_cap > 10_000_000_000:
                if user.risk_tier == "intermediate":
                    score += 15
                risk_level = "medium"
            else:
                if user.risk_tier == "advanced":
                    score += 15
                    reasons.append("Growth-stage opportunity")
                risk_level = "high"

        risk_flags = self.db.query(RiskFlag).filter(
            RiskFlag.company_id == company.id, RiskFlag.is_active == True
        ).all()
        avg_risk = sum(f.severity_score or 0 for f in risk_flags) / len(risk_flags) if risk_flags else 30

        if avg_risk < 40:
            score += 15
            reasons.append("Low risk profile")
        elif avg_risk > 70 and user.risk_tier == "beginner":
            score -= 20
            reasons.append("High risk — not recommended for beginners")

        recent_news = (
            self.db.query(NewsArticle)
            .join(NewsCompany)
            .filter(NewsCompany.company_id == company.id)
            .filter(NewsArticle.published_at >= datetime.utcnow() - timedelta(days=7))
            .count()
        )
        if recent_news > 3:
            score += 10
            reasons.append("Active in recent news")

        match_type = "diversification" if "sector diversification" in str(reasons) else \
                     "risk_match" if "suits your tier" in str(reasons) else "general"

        return {"total": max(0, score), "reasons": reasons, "risk_level": risk_level, "match_type": match_type}

    def _sector_risk_profile(self, sector_id: int) -> str:
        companies = self.db.query(Company).filter(Company.sector_id == sector_id, Company.is_active == True).limit(20).all()
        if not companies:
            return "unknown"
        company_ids = [c.id for c in companies]
        flags = self.db.query(RiskFlag).filter(RiskFlag.company_id.in_(company_ids), RiskFlag.is_active == True).all()
        if not flags:
            return "low"
        avg = sum(f.severity_score or 0 for f in flags) / len(flags)
        if avg > 60:
            return "high"
        elif avg > 35:
            return "medium"
        return "low"

    def _get_watchlist_companies(self, min_cap: float = 0, max_cap: float = None,
                                 company_type: str = None, limit: int = 8) -> List[Dict]:
        query = self.db.query(Company).filter(Company.is_active == True)
        if min_cap:
            query = query.filter(Company.market_cap >= min_cap)
        if max_cap:
            query = query.filter(Company.market_cap <= max_cap)
        if company_type:
            query = query.filter(Company.company_type == company_type)

        companies = query.order_by(Company.market_cap.desc().nullslast()).limit(limit).all()
        return [{"id": c.id, "name": c.name, "ticker": c.ticker, "type": c.company_type} for c in companies]

    def _get_trending_companies(self, limit: int = 6) -> List[Dict]:
        cutoff = datetime.utcnow() - timedelta(days=7)
        trending = (
            self.db.query(NewsCompany.company_id, func.count(NewsCompany.news_id).label("mention_count"))
            .join(NewsArticle)
            .filter(NewsArticle.published_at >= cutoff)
            .group_by(NewsCompany.company_id)
            .order_by(desc("mention_count"))
            .limit(limit)
            .all()
        )

        results = []
        for company_id, count in trending:
            company = self.db.query(Company).filter(Company.id == company_id).first()
            if company:
                results.append({"id": company.id, "name": company.name, "ticker": company.ticker, "mentions": count})
        return results
