"""
FinBERT-based sentiment analysis for news headlines and social posts.
"""
from typing import Literal


SentimentLabel = Literal["bullish", "bearish", "neutral"]


class SentimentResult:
    def __init__(self, label: SentimentLabel, confidence: float):
        self.label = label
        self.confidence = confidence


async def analyze_sentiment(text: str) -> SentimentResult:
    """
    Runs FinBERT sentiment analysis on a text string.
    In production, loads the FinBERT model or calls a model serving endpoint.
    """
    # Placeholder: In production, use transformers pipeline
    # from transformers import pipeline
    # nlp = pipeline("sentiment-analysis", model="ProsusAI/finbert")
    # result = nlp(text)[0]

    text_lower = text.lower()
    if any(w in text_lower for w in ["beat", "strong", "growth", "upgrade", "record"]):
        return SentimentResult(label="bullish", confidence=0.78)
    elif any(w in text_lower for w in ["miss", "downgrade", "risk", "decline", "sell"]):
        return SentimentResult(label="bearish", confidence=0.72)
    return SentimentResult(label="neutral", confidence=0.60)


async def batch_analyze(texts: list[str]) -> list[SentimentResult]:
    """Analyze sentiment for multiple texts."""
    return [await analyze_sentiment(t) for t in texts]
