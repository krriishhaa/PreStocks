"""
LangGraph workflow: Provides trade advice given portfolio context.
Uses Claude API for personalized guidance.
"""
from typing import TypedDict


class TradeAdvisorState(TypedDict):
    user_id: str
    ticker: str
    action: str
    shares: float
    portfolio_summary: dict
    risk_flags: list
    user_tier: str
    advice: str


async def advise_trade(state: TradeAdvisorState) -> TradeAdvisorState:
    """
    Generates personalized trade advice considering portfolio composition,
    risk flags, and user experience level.
    """
    flags_summary = ", ".join(
        f"{f['category']}({f['score']})" for f in state['risk_flags'][:5]
    ) if state['risk_flags'] else "none active"

    system_prompt = f"""You are a cautious financial education advisor for PreStocks (paper trading).
Never give direct buy/sell recommendations. Instead, surface relevant considerations.

Context:
- User tier: {state['user_tier']}
- Action: {state['action']} {state['shares']} shares of {state['ticker']}
- Portfolio value: ${state['portfolio_summary'].get('total_value', 0):,.2f}
- Cash available: ${state['portfolio_summary'].get('cash_balance', 0):,.2f}
- Active risk flags: {flags_summary}

Provide 2-3 bullet points of considerations (not recommendations)."""

    # In production, call Claude API:
    # from anthropic import AsyncAnthropic
    # client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    # response = await client.messages.create(...)

    position_value = state['shares'] * 150  # mock price
    portfolio_pct = (position_value / state['portfolio_summary'].get('total_value', 1)) * 100

    state["advice"] = (
        f"• This trade would represent ~{portfolio_pct:.1f}% of your portfolio.\n"
        f"• Current risk flags ({flags_summary}) suggest elevated caution.\n"
        f"• Consider your overall sector exposure and diversification goals."
    )
    return state
