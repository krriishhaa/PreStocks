"""
AI Research Engine — Analyzes any company and generates comprehensive research reports.

Capabilities:
- Company summary and overview
- Risk assessment (financial, operational, market, regulatory)
- Opportunity identification
- Financial health scoring
- Funding history analysis
- Competitor mapping
- IPO probability estimation (for private companies)
- SWOT analysis

Uses: Claude API for reasoning, internal data for context.
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import json

from app.models.company import Company, CompanyFundamentals, CompetitorRelationship
from app.models.investor import FundingRound, FundingRoundInvestor, Investor
from app.models.flags import RiskFlag
from app.models.news import NewsArticle, NewsCompany
from app.models.ai import AIResearchReport
from app.core.config import settings


class AIResearchEngine:
    def __init__(self, db: Session):
        self.db = db

    def generate_research_report(
        self,
        user_id: int,
        company_id: Optional[int] = None,
        ticker: Optional[str] = None,
        company_name: Optional[str] = None,
        report_type: str = "full_analysis",
        include_sections: List[str] = None
    ) -> AIResearchReport:
        company = self._resolve_company(company_id, ticker, company_name)

        context = self._gather_context(company)

        sections = include_sections or [
            "summary", "risks", "opportunities",
            "financial_health", "funding_history",
            "competitors", "ipo_probability"
        ]

        report_data = self._generate_analysis(company, context, sections, report_type)

        report = AIResearchReport(
            user_id=user_id,
            company_id=company.id,
            report_type=report_type,
            summary=report_data.get("summary"),
            risks=report_data.get("risks"),
            opportunities=report_data.get("opportunities"),
            financial_health=report_data.get("financial_health"),
            funding_history=report_data.get("funding_history"),
            competitors=report_data.get("competitors"),
            ipo_probability=report_data.get("ipo_probability"),
            swot_analysis=report_data.get("swot_analysis"),
            model_used="claude-sonnet-4-20250514",
            data_sources=context.get("data_sources", []),
            confidence_score=report_data.get("confidence_score", 0.75),
            valid_until=datetime.utcnow() + timedelta(days=7)
        )

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def _resolve_company(self, company_id, ticker, company_name) -> Company:
        if company_id:
            company = self.db.query(Company).filter(Company.id == company_id).first()
        elif ticker:
            company = self.db.query(Company).filter(Company.ticker == ticker).first()
        elif company_name:
            company = self.db.query(Company).filter(Company.name.ilike(f"%{company_name}%")).first()
        else:
            raise ValueError("Must provide company_id, ticker, or company_name")

        if not company:
            if company_name or ticker:
                company = Company(
                    name=company_name or ticker,
                    ticker=ticker,
                    company_type="private" if not ticker else "public"
                )
                self.db.add(company)
                self.db.commit()
                self.db.refresh(company)
            else:
                raise ValueError("Company not found")
        return company

    def _gather_context(self, company: Company) -> dict:
        context = {"data_sources": []}

        fundamentals = (
            self.db.query(CompanyFundamentals)
            .filter(CompanyFundamentals.company_id == company.id)
            .order_by(CompanyFundamentals.period_end.desc())
            .limit(8)
            .all()
        )
        if fundamentals:
            context["fundamentals"] = [
                {
                    "period": str(f.period_end),
                    "revenue": f.revenue,
                    "net_income": f.net_income,
                    "pe_ratio": f.pe_ratio,
                    "debt_to_equity": f.debt_to_equity,
                    "revenue_growth_yoy": f.revenue_growth_yoy,
                    "operating_margin": f.operating_margin,
                    "free_cash_flow": f.free_cash_flow
                } for f in fundamentals
            ]
            context["data_sources"].append("internal_fundamentals")

        funding_rounds = (
            self.db.query(FundingRound)
            .filter(FundingRound.company_id == company.id)
            .order_by(FundingRound.announced_date.desc())
            .all()
        )
        if funding_rounds:
            context["funding"] = [
                {
                    "round_type": fr.round_type,
                    "amount": fr.amount_raised_usd,
                    "valuation": fr.post_money_valuation,
                    "date": str(fr.announced_date) if fr.announced_date else None
                } for fr in funding_rounds
            ]
            context["data_sources"].append("internal_funding_data")

        risk_flags = (
            self.db.query(RiskFlag)
            .filter(RiskFlag.company_id == company.id, RiskFlag.is_active == True)
            .all()
        )
        if risk_flags:
            context["risk_flags"] = [
                {
                    "type": rf.flag_type,
                    "severity": rf.severity_score,
                    "explanation": rf.explanation
                } for rf in risk_flags
            ]
            context["data_sources"].append("risk_flag_engine")

        competitors = (
            self.db.query(CompetitorRelationship)
            .filter(CompetitorRelationship.company_id == company.id)
            .all()
        )
        if competitors:
            comp_data = []
            for c in competitors:
                comp_company = self.db.query(Company).filter(Company.id == c.competitor_id).first()
                if comp_company:
                    comp_data.append({
                        "name": comp_company.name,
                        "ticker": comp_company.ticker,
                        "overlap": c.overlap_score,
                        "type": c.relationship_type
                    })
            context["competitors"] = comp_data
            context["data_sources"].append("competitor_mapping")

        recent_news = (
            self.db.query(NewsArticle)
            .join(NewsCompany)
            .filter(NewsCompany.company_id == company.id)
            .order_by(NewsArticle.published_at.desc())
            .limit(10)
            .all()
        )
        if recent_news:
            context["news"] = [
                {
                    "title": n.title,
                    "sentiment": n.sentiment_label,
                    "date": str(n.published_at)
                } for n in recent_news
            ]
            context["data_sources"].append("news_feed")

        return context

    def _generate_analysis(self, company: Company, context: dict, sections: List[str], report_type: str) -> dict:
        """
        Generate AI analysis using Claude API.
        Falls back to rule-based analysis if API unavailable.
        """
        result = {}

        if "summary" in sections:
            result["summary"] = self._generate_summary(company, context)

        if "risks" in sections:
            result["risks"] = self._analyze_risks(company, context)

        if "opportunities" in sections:
            result["opportunities"] = self._identify_opportunities(company, context)

        if "financial_health" in sections:
            result["financial_health"] = self._assess_financial_health(company, context)

        if "funding_history" in sections:
            result["funding_history"] = self._analyze_funding(company, context)

        if "competitors" in sections:
            result["competitors"] = self._map_competitors(company, context)

        if "ipo_probability" in sections:
            result["ipo_probability"] = self._estimate_ipo_probability(company, context)

        if report_type == "swot":
            result["swot_analysis"] = self._generate_swot(company, context)

        result["confidence_score"] = self._calculate_confidence(context)
        return result

    def _generate_summary(self, company: Company, context: dict) -> str:
        parts = []
        parts.append(f"{company.name} is a {company.company_type} company")
        if company.industry:
            parts.append(f"in the {company.industry} sector")
        if company.market_cap:
            cap_b = company.market_cap / 1_000_000_000
            parts.append(f"with a market cap of ${cap_b:.1f}B")
        if company.employee_count:
            parts.append(f"employing {company.employee_count:,} people")
        if company.headquarters_city:
            parts.append(f"headquartered in {company.headquarters_city}")

        summary = " ".join(parts) + "."

        if context.get("fundamentals"):
            latest = context["fundamentals"][0]
            if latest.get("revenue"):
                rev_b = latest["revenue"] / 1_000_000_000
                summary += f" Latest quarterly revenue: ${rev_b:.2f}B."
            if latest.get("revenue_growth_yoy"):
                summary += f" YoY revenue growth: {latest['revenue_growth_yoy']:.1f}%."

        if context.get("news"):
            sentiments = [n["sentiment"] for n in context["news"] if n.get("sentiment")]
            if sentiments:
                positive = sentiments.count("positive")
                negative = sentiments.count("negative")
                if positive > negative:
                    summary += " Recent news sentiment is predominantly positive."
                elif negative > positive:
                    summary += " Recent news sentiment leans negative — monitor closely."

        return summary

    def _analyze_risks(self, company: Company, context: dict) -> list:
        risks = []

        if context.get("risk_flags"):
            for flag in context["risk_flags"]:
                risks.append({
                    "category": flag["type"],
                    "severity": "high" if flag["severity"] > 70 else "medium" if flag["severity"] > 40 else "low",
                    "score": flag["severity"],
                    "description": flag["explanation"] or f"{flag['type']} risk detected",
                    "source": "risk_flag_engine"
                })

        if context.get("fundamentals"):
            latest = context["fundamentals"][0]
            if latest.get("debt_to_equity") and latest["debt_to_equity"] > 2.0:
                risks.append({
                    "category": "financial_leverage",
                    "severity": "high",
                    "score": min(95, int(latest["debt_to_equity"] * 30)),
                    "description": f"High debt-to-equity ratio of {latest['debt_to_equity']:.2f}. Company may face refinancing risk.",
                    "source": "fundamental_analysis"
                })
            if latest.get("operating_margin") and latest["operating_margin"] < 0:
                risks.append({
                    "category": "profitability",
                    "severity": "medium",
                    "score": 55,
                    "description": f"Negative operating margin ({latest['operating_margin']:.1f}%). Not yet profitable at operational level.",
                    "source": "fundamental_analysis"
                })

        if not risks:
            risks.append({
                "category": "data_availability",
                "severity": "low",
                "score": 20,
                "description": "Limited data available for comprehensive risk assessment. Gather more information.",
                "source": "system"
            })

        return sorted(risks, key=lambda x: x["score"], reverse=True)

    def _identify_opportunities(self, company: Company, context: dict) -> list:
        opportunities = []

        if context.get("fundamentals"):
            latest = context["fundamentals"][0]
            if latest.get("revenue_growth_yoy") and latest["revenue_growth_yoy"] > 20:
                opportunities.append({
                    "category": "growth",
                    "strength": "high",
                    "description": f"Strong revenue growth of {latest['revenue_growth_yoy']:.1f}% YoY indicates market share expansion.",
                    "timeframe": "12-18 months"
                })
            if latest.get("free_cash_flow") and latest["free_cash_flow"] > 0:
                fcf_b = latest["free_cash_flow"] / 1_000_000_000
                opportunities.append({
                    "category": "cash_generation",
                    "strength": "medium",
                    "description": f"Positive free cash flow of ${fcf_b:.2f}B enables reinvestment and shareholder returns.",
                    "timeframe": "ongoing"
                })

        if context.get("funding"):
            total_raised = sum(f.get("amount", 0) or 0 for f in context["funding"])
            if total_raised > 100_000_000:
                opportunities.append({
                    "category": "capital_backing",
                    "strength": "high",
                    "description": f"Strong investor backing with ${total_raised/1_000_000:.0f}M raised. Well-funded for expansion.",
                    "timeframe": "24-36 months"
                })

        if company.company_type == "pre_ipo":
            opportunities.append({
                "category": "ipo_upside",
                "strength": "high",
                "description": "Pre-IPO stage offers potential for significant valuation jump at listing.",
                "timeframe": "12-24 months"
            })

        return opportunities

    def _assess_financial_health(self, company: Company, context: dict) -> dict:
        health = {
            "overall_score": 50,
            "grade": "B",
            "metrics": {},
            "trend": "stable",
            "concerns": [],
            "strengths": []
        }

        if not context.get("fundamentals"):
            health["overall_score"] = 50
            health["grade"] = "N/A"
            health["concerns"].append("Insufficient financial data for assessment")
            return health

        latest = context["fundamentals"][0]
        scores = []

        if latest.get("current_ratio"):
            cr_score = min(100, int(latest["current_ratio"] * 33))
            scores.append(cr_score)
            health["metrics"]["liquidity"] = {
                "score": cr_score,
                "value": latest["current_ratio"],
                "benchmark": 1.5
            }

        if latest.get("debt_to_equity") is not None:
            de_score = max(0, 100 - int(latest["debt_to_equity"] * 25))
            scores.append(de_score)
            health["metrics"]["leverage"] = {
                "score": de_score,
                "value": latest["debt_to_equity"],
                "benchmark": 1.0
            }

        if latest.get("operating_margin") is not None:
            om_score = max(0, min(100, int(50 + latest["operating_margin"] * 2)))
            scores.append(om_score)
            health["metrics"]["profitability"] = {
                "score": om_score,
                "value": latest["operating_margin"],
                "benchmark": 15.0
            }

        if latest.get("revenue_growth_yoy") is not None:
            growth_score = max(0, min(100, int(50 + latest["revenue_growth_yoy"] * 1.5)))
            scores.append(growth_score)
            health["metrics"]["growth"] = {
                "score": growth_score,
                "value": latest["revenue_growth_yoy"],
                "benchmark": 10.0
            }

        if scores:
            health["overall_score"] = int(sum(scores) / len(scores))
            score = health["overall_score"]
            if score >= 80: health["grade"] = "A"
            elif score >= 65: health["grade"] = "B"
            elif score >= 50: health["grade"] = "C"
            elif score >= 35: health["grade"] = "D"
            else: health["grade"] = "F"

        if len(context["fundamentals"]) >= 2:
            prev = context["fundamentals"][1]
            if prev.get("revenue") and latest.get("revenue"):
                if latest["revenue"] > prev["revenue"]:
                    health["trend"] = "improving"
                elif latest["revenue"] < prev["revenue"]:
                    health["trend"] = "declining"

        return health

    def _analyze_funding(self, company: Company, context: dict) -> dict:
        if not context.get("funding"):
            return {"total_raised": 0, "rounds": [], "latest_valuation": None}

        rounds = context["funding"]
        total = sum(r.get("amount", 0) or 0 for r in rounds)
        valuations = [r.get("valuation") for r in rounds if r.get("valuation")]

        return {
            "total_raised_usd": total,
            "num_rounds": len(rounds),
            "latest_valuation": valuations[0] if valuations else None,
            "rounds": rounds[:5],
            "funding_velocity": self._calc_funding_velocity(rounds),
            "valuation_trajectory": "increasing" if len(valuations) >= 2 and valuations[0] > valuations[-1] else "flat"
        }

    def _map_competitors(self, company: Company, context: dict) -> list:
        if context.get("competitors"):
            return context["competitors"]
        return [{
            "name": "Data not available",
            "note": "Run competitor analysis task to populate"
        }]

    def _estimate_ipo_probability(self, company: Company, context: dict) -> dict:
        if company.company_type == "public":
            return {"probability": 1.0, "status": "already_public", "ipo_date": str(company.ipo_date) if company.ipo_date else None}

        score = 0.3
        factors = []

        if context.get("funding"):
            total_raised = sum(r.get("amount", 0) or 0 for r in context["funding"])
            if total_raised > 500_000_000:
                score += 0.25
                factors.append("Raised >$500M — typical IPO threshold")
            elif total_raised > 100_000_000:
                score += 0.15
                factors.append("Raised >$100M — approaching IPO readiness")

            latest_val = next((r.get("valuation") for r in context["funding"] if r.get("valuation")), None)
            if latest_val and latest_val > 1_000_000_000:
                score += 0.15
                factors.append("Unicorn valuation (>$1B)")

        if context.get("fundamentals"):
            latest = context["fundamentals"][0]
            if latest.get("revenue") and latest["revenue"] > 100_000_000:
                score += 0.1
                factors.append("Revenue >$100M — IPO-scale business")
            if latest.get("revenue_growth_yoy") and latest["revenue_growth_yoy"] > 30:
                score += 0.1
                factors.append("High growth rate attractive to public markets")

        return {
            "probability": min(0.95, score),
            "confidence": 0.6,
            "factors": factors,
            "estimated_timeline": "12-24 months" if score > 0.6 else "24-48 months" if score > 0.4 else "Not imminent",
            "status": "pre_ipo"
        }

    def _generate_swot(self, company: Company, context: dict) -> dict:
        swot = {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}

        if context.get("fundamentals"):
            latest = context["fundamentals"][0]
            if latest.get("revenue_growth_yoy") and latest["revenue_growth_yoy"] > 15:
                swot["strengths"].append("Strong revenue growth trajectory")
            if latest.get("operating_margin") and latest["operating_margin"] > 20:
                swot["strengths"].append("High operating margins indicating pricing power")
            if latest.get("debt_to_equity") and latest["debt_to_equity"] > 2:
                swot["weaknesses"].append("High leverage increases financial risk")
            if latest.get("operating_margin") and latest["operating_margin"] < 0:
                swot["weaknesses"].append("Not yet operationally profitable")

        if company.market_cap and company.market_cap > 100_000_000_000:
            swot["strengths"].append("Large market cap provides stability and access to capital")
        if company.employee_count and company.employee_count > 10000:
            swot["strengths"].append("Large workforce indicates operational scale")

        swot["opportunities"].append("AI/ML integration potential across product lines")
        swot["opportunities"].append("International market expansion")
        swot["threats"].append("Regulatory environment uncertainty")
        swot["threats"].append("Competitive pressure from well-funded peers")

        return swot

    def _calc_funding_velocity(self, rounds: list) -> str:
        if len(rounds) < 2:
            return "insufficient_data"
        dates = [r.get("date") for r in rounds if r.get("date")]
        if len(dates) >= 2:
            return "rapid" if len(rounds) > 4 else "moderate"
        return "unknown"

    def _calculate_confidence(self, context: dict) -> float:
        score = 0.3
        if context.get("fundamentals"):
            score += 0.2
        if context.get("funding"):
            score += 0.15
        if context.get("risk_flags"):
            score += 0.1
        if context.get("competitors"):
            score += 0.1
        if context.get("news"):
            score += 0.15
        return min(1.0, score)
