from __future__ import annotations

from collections import Counter
import re


def analyze_sec_filing(filing_type: str, text: str) -> dict:
    filing_type = filing_type.upper().strip()
    normalized = _normalize(text)
    sentences = _sentences(normalized)

    risk_terms = [
        "risk",
        "lawsuit",
        "regulatory",
        "volatility",
        "inflation",
        "supply chain",
        "competition",
        "debt",
    ]
    opportunity_terms = [
        "growth",
        "expansion",
        "innovation",
        "partnership",
        "ai",
        "margin",
        "efficiency",
        "market share",
    ]
    management_terms = ["management", "executive", "strategy", "guidance", "outlook", "we expect"]
    moat_terms = ["patent", "brand", "network effects", "switching costs", "proprietary", "scale"]

    return {
        "filing_type": filing_type,
        "risks": _top_hits(sentences, risk_terms),
        "opportunities": _top_hits(sentences, opportunity_terms),
        "management_commentary": _top_hits(sentences, management_terms),
        "competitive_advantages": _top_hits(sentences, moat_terms),
        "signal_counts": _count_signals(normalized, risk_terms + opportunity_terms + moat_terms),
    }


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[\.\!\?])\s+", text)
    return [s.strip() for s in parts if s.strip()]


def _top_hits(sentences: list[str], keywords: list[str], limit: int = 5) -> list[str]:
    scored = []
    for sentence in sentences:
        score = sum(1 for kw in keywords if kw in sentence.lower())
        if score > 0:
            scored.append((score, sentence))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:limit]]


def _count_signals(text: str, keywords: list[str]) -> dict[str, int]:
    counts = Counter()
    lower = text.lower()
    for kw in keywords:
        counts[kw] = lower.count(kw)
    return dict(counts)

