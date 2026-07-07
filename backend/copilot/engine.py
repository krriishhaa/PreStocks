from __future__ import annotations

from typing import Any


AI_BENEFICIARY_UNIVERSE = [
    {"symbol": "NVDA", "theme_score": 0.95, "reason": "Core AI compute and datacenter accelerator leader"},
    {"symbol": "MSFT", "theme_score": 0.87, "reason": "AI cloud platform + enterprise software distribution"},
    {"symbol": "GOOGL", "theme_score": 0.81, "reason": "AI search, cloud, and foundational model investments"},
    {"symbol": "AMZN", "theme_score": 0.79, "reason": "AWS AI services and automation scale"},
    {"symbol": "AVGO", "theme_score": 0.76, "reason": "Networking and custom silicon for AI infrastructure"},
]


def run_copilot(question: str, risk_profile: str = "moderate") -> dict[str, Any]:
    q = (question or "").lower()
    if "benefit from ai" in q or ("ai" in q and "stock" in q):
        return _ai_beneficiary_answer(question)
    if "retirement portfolio" in q or "retirement" in q:
        return _retirement_portfolio_answer(risk_profile)
    return {
        "question": question,
        "workflow": ["search", "analyze", "rank", "explain"],
        "answer": "Copilot received the query. Ask about AI beneficiary stocks or retirement portfolio construction.",
    }


def _ai_beneficiary_answer(question: str) -> dict[str, Any]:
    ranked = sorted(AI_BENEFICIARY_UNIVERSE, key=lambda x: x["theme_score"], reverse=True)
    return {
        "question": question,
        "workflow": ["search", "analyze", "rank", "explain"],
        "ranked_stocks": ranked,
        "answer": (
            "Top AI beneficiaries are ranked by ecosystem leverage, compute demand exposure, and pricing power. "
            "NVIDIA and Microsoft lead due to direct monetization of AI demand across hardware and cloud."
        ),
    }


def _retirement_portfolio_answer(risk_profile: str) -> dict[str, Any]:
    allocations = {
        "conservative": {"bonds": 50, "us_equity": 30, "intl_equity": 15, "reits": 5},
        "moderate": {"bonds": 30, "us_equity": 45, "intl_equity": 20, "reits": 5},
        "aggressive": {"bonds": 10, "us_equity": 60, "intl_equity": 25, "reits": 5},
    }.get(risk_profile.lower(), {"bonds": 30, "us_equity": 45, "intl_equity": 20, "reits": 5})

    return {
        "question": "Build a retirement portfolio",
        "workflow": ["risk analysis", "allocation", "diversification", "tax considerations"],
        "risk_profile": risk_profile,
        "allocation": allocations,
        "tax_considerations": [
            "Place bonds in tax-advantaged accounts where possible.",
            "Use tax-loss harvesting for taxable equity accounts.",
            "Prefer broad ETFs for turnover and tax efficiency.",
        ],
        "answer": (
            "Portfolio is diversified across equity, international exposure, and fixed income based on risk profile. "
            "Tax-aware placement is included to improve after-tax retirement outcomes."
        ),
    }

