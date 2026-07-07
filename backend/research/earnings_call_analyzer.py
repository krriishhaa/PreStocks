from __future__ import annotations

import re


def analyze_earnings_call(transcript: str) -> dict:
    text = _normalize(transcript)
    sentiment = _sentiment(text)
    guidance = _guidance_changes(text)
    ceo_conf = _ceo_confidence(text)
    risk_factors = _extract_risk_factors(text)
    return {
        "sentiment": sentiment,
        "guidance_changes": guidance,
        "ceo_confidence": ceo_conf,
        "risk_factors": risk_factors,
    }


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _sentiment(text: str) -> dict:
    bullish = ["strong", "accelerating", "record", "confident", "expansion", "beat", "upside"]
    bearish = ["uncertain", "headwind", "decline", "pressure", "weak", "risk", "conservative"]
    lower = text.lower()
    bull_hits = sum(lower.count(word) for word in bullish)
    bear_hits = sum(lower.count(word) for word in bearish)
    net = bull_hits - bear_hits
    label = "neutral"
    if net > 2:
        label = "bullish"
    elif net < -2:
        label = "bearish"
    return {"label": label, "bullish_hits": bull_hits, "bearish_hits": bear_hits, "net_score": net}


def _guidance_changes(text: str) -> list[str]:
    patterns = [
        r"(raised guidance[^\.]*\.)",
        r"(lowered guidance[^\.]*\.)",
        r"(updated outlook[^\.]*\.)",
        r"(reaffirmed guidance[^\.]*\.)",
    ]
    findings: list[str] = []
    for pattern in patterns:
        findings.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    return findings[:8]


def _ceo_confidence(text: str) -> dict:
    confidence_terms = ["confident", "visibility", "execution", "on track", "strong pipeline"]
    uncertainty_terms = ["uncertain", "challenging", "limited visibility", "volatile", "cautious"]
    lower = text.lower()
    conf = sum(lower.count(term) for term in confidence_terms)
    unc = sum(lower.count(term) for term in uncertainty_terms)
    score = conf - unc
    level = "medium"
    if score >= 3:
        level = "high"
    elif score <= -1:
        level = "low"
    return {"level": level, "score": score, "confidence_hits": conf, "uncertainty_hits": unc}


def _extract_risk_factors(text: str) -> list[str]:
    risk_words = [
        "macro",
        "regulation",
        "pricing pressure",
        "supply chain",
        "currency",
        "demand softness",
        "competition",
        "litigation",
    ]
    sentences = re.split(r"(?<=[\.\!\?])\s+", text)
    hits = [s.strip() for s in sentences if any(word in s.lower() for word in risk_words)]
    return hits[:8]

