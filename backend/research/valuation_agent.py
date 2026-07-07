from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ValuationInput:
    symbol: str
    price: float
    shares_outstanding: float
    free_cash_flow: float
    growth_rate: float
    discount_rate: float
    terminal_growth: float
    eps: float
    earnings_growth_rate: float
    ebitda: float
    enterprise_value: float
    revenue_growth: float
    profit_margin: float


def compute_valuation_metrics(v: ValuationInput) -> dict:
    intrinsic_value = _dcf_value(v)
    market_cap = v.price * v.shares_outstanding if v.shares_outstanding > 0 else 0.0
    pe = v.price / v.eps if v.eps > 0 else None
    peg = pe / (v.earnings_growth_rate * 100) if pe and v.earnings_growth_rate > 0 else None
    ev_ebitda = v.enterprise_value / v.ebitda if v.ebitda > 0 else None
    rule_of_40 = (v.revenue_growth * 100) + (v.profit_margin * 100)
    valuation_label = _valuation_label(v.price, intrinsic_value)
    explanation = _explain_valuation(v, intrinsic_value, pe, peg, ev_ebitda, rule_of_40)

    return {
        "symbol": v.symbol.upper(),
        "market_cap": round(market_cap, 2),
        "dcf_intrinsic_value_per_share": round(intrinsic_value, 2),
        "pe": round(pe, 2) if pe else None,
        "peg": round(peg, 2) if peg else None,
        "ev_ebitda": round(ev_ebitda, 2) if ev_ebitda else None,
        "rule_of_40": round(rule_of_40, 2),
        "valuation_label": valuation_label,
        "explanation": explanation,
    }


def _dcf_value(v: ValuationInput) -> float:
    # 5-year DCF projection with Gordon Growth terminal value.
    fcf = v.free_cash_flow
    pv_sum = 0.0
    for year in range(1, 6):
        fcf *= 1 + v.growth_rate
        pv_sum += fcf / ((1 + v.discount_rate) ** year)
    terminal = (fcf * (1 + v.terminal_growth)) / max(v.discount_rate - v.terminal_growth, 0.01)
    terminal_pv = terminal / ((1 + v.discount_rate) ** 5)
    total_value = pv_sum + terminal_pv
    if v.shares_outstanding <= 0:
        return 0.0
    return total_value / v.shares_outstanding


def _valuation_label(price: float, intrinsic_value: float) -> str:
    if intrinsic_value <= 0:
        return "indeterminate"
    diff_pct = (price - intrinsic_value) / intrinsic_value
    if diff_pct <= -0.15:
        return "cheap"
    if diff_pct >= 0.15:
        return "expensive"
    return "fair"


def _explain_valuation(
    v: ValuationInput,
    intrinsic_value: float,
    pe: float | None,
    peg: float | None,
    ev_ebitda: float | None,
    rule_of_40: float,
) -> str:
    reasons: list[str] = []
    if intrinsic_value > v.price:
        reasons.append("DCF suggests upside versus current price.")
    else:
        reasons.append("DCF suggests limited upside at current price.")

    if pe and pe < 18:
        reasons.append("P/E is in a lower range for growth equities.")
    elif pe and pe > 30:
        reasons.append("P/E indicates premium expectations are priced in.")

    if peg and peg < 1.0:
        reasons.append("PEG under 1.0 implies growth is inexpensive.")
    elif peg and peg > 2.0:
        reasons.append("PEG above 2.0 signals expensive growth.")

    if ev_ebitda and ev_ebitda > 18:
        reasons.append("EV/EBITDA is elevated versus traditional value thresholds.")

    if rule_of_40 >= 40:
        reasons.append("Rule of 40 score supports durable growth + profitability.")
    else:
        reasons.append("Rule of 40 score suggests growth/profitability balance needs work.")

    return " ".join(reasons)

