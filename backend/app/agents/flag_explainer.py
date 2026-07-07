"""
LangGraph Flag Explanation Agent.
Multi-step workflow:
1. Retrieve flag details
2. Fetch historical context (similar periods)
3. Generate plain-English explanation via Claude
4. Provide actionable guidance
"""
from typing import TypedDict, Optional
from datetime import datetime, timezone

from langgraph.graph import StateGraph, START, END


class FlagExplainerState(TypedDict):
    stock_id: int
    flag_type: str
    user_tier: str
    flag: Optional[dict]
    historical_context: Optional[list]
    explanation: Optional[str]
    guidance: Optional[str]


def create_flag_explainer_agent():
    """
    Creates the compiled LangGraph workflow for flag explanation.
    """
    graph = StateGraph(FlagExplainerState)

    # Step 1: Retrieve the flag details
    def retrieve_flag(state: FlagExplainerState) -> FlagExplainerState:
        """Fetch the current flag data from DB/cache."""
        from app.utils.redis_cache import RedisCache
        import asyncio

        stock_id = state["stock_id"]
        flag_type = state["flag_type"]

        # In production: query the risk_flag table
        # flag = db.query(RiskFlag).filter_by(stock_id=stock_id, flag_type=flag_type).first()
        state["flag"] = {
            "stock_id": stock_id,
            "flag_type": flag_type,
            "severity_score": 72,
            "explanation": f"The {flag_type} flag is elevated for this stock.",
            "confidence_score": 0.85,
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }
        return state

    # Step 2: Fetch historical context
    def get_historical_context(state: FlagExplainerState) -> FlagExplainerState:
        """
        Get similar periods in history where this flag was triggered.
        Useful for showing "last time this happened, here's what followed."
        """
        stock_id = state["stock_id"]
        flag_type = state["flag_type"]

        # In production: query flag_history or risk_flag archive
        # historical = db.query(RiskFlag).filter_by(
        #     stock_id=stock_id, flag_type=flag_type
        # ).order_by(RiskFlag.calculated_at.desc()).limit(5).all()

        state["historical_context"] = [
            {"date": "2024-03-15", "score": 68, "outcome_30d": "-8.2%"},
            {"date": "2023-11-20", "score": 75, "outcome_30d": "-12.1%"},
            {"date": "2023-06-05", "score": 61, "outcome_30d": "+3.4%"},
        ]
        return state

    # Step 3: Generate explanation via Claude
    def generate_explanation(state: FlagExplainerState) -> FlagExplainerState:
        """
        Use Claude to generate a user-friendly explanation.
        Adjusts complexity based on user tier.
        """
        from app.core.config import get_settings
        settings = get_settings()

        flag = state["flag"]
        historical = state["historical_context"]
        user_tier = state["user_tier"]

        tier_instruction = {
            "beginner": "Explain in very simple terms, as if to someone who just started learning about stocks. Use analogies and avoid jargon.",
            "intermediate": "Explain concisely with relevant technical context. Assume basic financial literacy.",
            "advanced": "Give a brief, data-driven explanation with quantitative details and actionable insight.",
        }.get(user_tier, "Explain in simple terms.")

        historical_summary = "\n".join(
            f"- {h['date']}: Flag score {h['score']}, 30-day outcome: {h['outcome_30d']}"
            for h in (historical or [])
        )

        prompt = f"""
{tier_instruction}

A user is viewing a stock and wants to understand this risk flag:
- Flag type: {flag['flag_type']}
- Severity: {flag['severity_score']}/100
- Current explanation: {flag['explanation']}

Historical context — when this flag was triggered before:
{historical_summary}

Provide a clear explanation in 2-3 sentences:
1. What caused this flag to trigger
2. Why it matters for this specific stock
3. What happened historically when this flag appeared

Do NOT give investment advice. Focus on education and context.
"""

        # In production, call Claude API:
        if settings.ANTHROPIC_API_KEY:
            # from anthropic import Anthropic
            # client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            # response = client.messages.create(
            #     model="claude-sonnet-4-20250514",
            #     max_tokens=300,
            #     messages=[{"role": "user", "content": prompt}]
            # )
            # state["explanation"] = response.content[0].text
            pass

        # Fallback explanation when API key not configured
        if not state.get("explanation"):
            flag_type = flag["flag_type"]
            score = flag["severity_score"]
            outcomes = [h["outcome_30d"] for h in (historical or [])]
            avg_outcome = "mixed results"
            if outcomes:
                negative = sum(1 for o in outcomes if o.startswith("-"))
                if negative > len(outcomes) / 2:
                    avg_outcome = "negative returns"
                else:
                    avg_outcome = "varied results"

            state["explanation"] = (
                f"The {flag_type} flag for this stock is at {score}/100, indicating elevated risk in this area. "
                f"Historically, when this flag was triggered at similar levels, the stock experienced {avg_outcome} over the following 30 days. "
                f"This doesn't predict the future, but it's worth understanding the risks involved."
            )

        return state

    # Step 4: Add actionable guidance
    def add_guidance(state: FlagExplainerState) -> FlagExplainerState:
        """Provide tier-appropriate actionable guidance based on flag type."""
        flag_type = state["flag_type"]
        user_tier = state["user_tier"]

        guidance_map = {
            "volatility": {
                "beginner": "Consider starting with a smaller position size. High volatility means the price can swing dramatically day-to-day.",
                "intermediate": "Size your position according to the volatility. A common approach is to risk no more than 1-2% of portfolio per trade.",
                "advanced": "Consider using options or stop-losses to manage downside. Position size inversely with realized vol.",
            },
            "valuation": {
                "beginner": "A high P/E means you're paying more per dollar of earnings. Compare to the company's own history and peers before deciding.",
                "intermediate": "Evaluate whether growth expectations justify the premium. Look at PEG ratio and forward estimates.",
                "advanced": "Assess earnings quality, FCF conversion, and compare EV/EBITDA multiples across peers. Consider the duration of growth.",
            },
            "balance_sheet": {
                "beginner": "Companies with high debt are riskier, especially during economic downturns. Check if they can cover their interest payments.",
                "intermediate": "Analyze the debt maturity schedule and interest coverage ratio. Rising rates increase refinancing risk.",
                "advanced": "Model the covenant headroom and stress-test under rising rates. Compare net-debt/EBITDA to sector norms.",
            },
            "insider_activity": {
                "beginner": "When company leaders sell their own stock, it can be a warning sign — but not always. Some sell for personal reasons.",
                "intermediate": "Distinguish between planned 10b5-1 sales and discretionary selling. Cluster selling by multiple insiders is more significant.",
                "advanced": "Cross-reference with option exercises, lockup expirations, and relative sale sizes. Look for pattern breaks.",
            },
            "momentum": {
                "beginner": "Stocks that have risen a lot recently may be due for a pullback. Don't chase performance — buy for the long term.",
                "intermediate": "Extended momentum can persist but reversals are sharp. Consider scaling in rather than buying all at once.",
                "advanced": "Monitor RSI, volume profile, and institutional flow. Mean-reversion signals strengthen above 2 standard deviations.",
            },
        }

        tier_guidance = guidance_map.get(flag_type, {})
        state["guidance"] = tier_guidance.get(user_tier, tier_guidance.get("beginner", "Review the fundamentals and risk factors before trading."))

        return state

    # Build the graph
    graph.add_node("retrieve_flag", retrieve_flag)
    graph.add_node("get_context", get_historical_context)
    graph.add_node("generate_explanation", generate_explanation)
    graph.add_node("add_guidance", add_guidance)

    graph.add_edge(START, "retrieve_flag")
    graph.add_edge("retrieve_flag", "get_context")
    graph.add_edge("get_context", "generate_explanation")
    graph.add_edge("generate_explanation", "add_guidance")
    graph.add_edge("add_guidance", END)

    return graph.compile()


# Convenience function
async def explain_flag_for_user(stock_id: int, flag_type: str, user_tier: str = "beginner") -> dict:
    """
    Run the full flag explanation workflow and return results.
    """
    agent = create_flag_explainer_agent()
    initial_state: FlagExplainerState = {
        "stock_id": stock_id,
        "flag_type": flag_type,
        "user_tier": user_tier,
        "flag": None,
        "historical_context": None,
        "explanation": None,
        "guidance": None,
    }
    result = agent.invoke(initial_state)
    return {
        "flag": result["flag"],
        "explanation": result["explanation"],
        "guidance": result["guidance"],
        "historical_context": result["historical_context"],
    }
