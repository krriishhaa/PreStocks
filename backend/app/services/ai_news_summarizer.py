"""
AI News Summarizer — Analyzes and summarizes news articles.

For every article, generates:
- Key points (3-5 bullet points)
- Sentiment classification with confidence
- Market impact assessment
- Affected companies and sectors
- Actionable recommendation
"""

from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from datetime import datetime

from app.models.news import NewsArticle, NewsCompany, NewsSector
from app.models.company import Company
from app.models.sector import Sector
from app.core.config import settings


class AINewsSummarizer:
    SENTIMENT_LABELS = {
        "very_positive": {"score_range": (0.7, 1.0), "market_impact": "strong_bullish"},
        "positive": {"score_range": (0.3, 0.7), "market_impact": "mildly_bullish"},
        "neutral": {"score_range": (-0.3, 0.3), "market_impact": "no_material_impact"},
        "negative": {"score_range": (-0.7, -0.3), "market_impact": "mildly_bearish"},
        "very_negative": {"score_range": (-1.0, -0.7), "market_impact": "strong_bearish"},
    }

    def __init__(self, db: Session):
        self.db = db

    def summarize_article(self, article_id: int) -> Dict:
        article = self.db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
        if not article:
            raise ValueError("Article not found")
        return self._analyze_article(article)

    def summarize_batch(self, article_ids: List[int]) -> List[Dict]:
        articles = self.db.query(NewsArticle).filter(NewsArticle.id.in_(article_ids)).all()
        return [self._analyze_article(a) for a in articles]

    def summarize_for_company(self, company_id: int, limit: int = 10) -> List[Dict]:
        articles = (
            self.db.query(NewsArticle)
            .join(NewsCompany)
            .filter(NewsCompany.company_id == company_id)
            .order_by(NewsArticle.published_at.desc())
            .limit(limit)
            .all()
        )
        return [self._analyze_article(a) for a in articles]

    def get_market_digest(self, hours: int = 24, limit: int = 15) -> Dict:
        """Generate a market-wide news digest."""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        articles = (
            self.db.query(NewsArticle)
            .filter(NewsArticle.published_at >= cutoff)
            .order_by(NewsArticle.relevance_score.desc().nullslast())
            .limit(limit)
            .all()
        )

        summaries = [self._analyze_article(a) for a in articles]

        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for s in summaries:
            label = s["sentiment"]["label"]
            if "positive" in label:
                sentiment_counts["positive"] += 1
            elif "negative" in label:
                sentiment_counts["negative"] += 1
            else:
                sentiment_counts["neutral"] += 1

        total = len(summaries)
        market_mood = "bullish" if sentiment_counts["positive"] > sentiment_counts["negative"] else \
                      "bearish" if sentiment_counts["negative"] > sentiment_counts["positive"] else "mixed"

        return {
            "period_hours": hours,
            "total_articles": total,
            "market_mood": market_mood,
            "sentiment_breakdown": sentiment_counts,
            "top_stories": summaries[:5],
            "all_summaries": summaries,
            "generated_at": datetime.utcnow().isoformat()
        }

    def _analyze_article(self, article: NewsArticle) -> Dict:
        key_points = self._extract_key_points(article)
        sentiment = self._classify_sentiment(article)
        market_impact = self._assess_market_impact(article, sentiment)
        affected = self._identify_affected_entities(article)
        recommendation = self._generate_recommendation(article, sentiment, market_impact)

        return {
            "article_id": article.id,
            "title": article.title,
            "source": article.source_name,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "key_points": key_points,
            "sentiment": sentiment,
            "market_impact": market_impact,
            "affected_entities": affected,
            "recommendation": recommendation,
            "is_breaking": article.is_breaking or False,
        }

    def _extract_key_points(self, article: NewsArticle) -> List[str]:
        """Extract 3-5 key points from article content."""
        points = []
        text = article.content or article.summary or article.title

        sentences = [s.strip() for s in text.replace("\n", ". ").split(".") if len(s.strip()) > 20]

        if not sentences:
            return [article.title]

        points.append(sentences[0] + ".")

        for s in sentences[1:6]:
            if any(kw in s.lower() for kw in ["revenue", "profit", "growth", "decline", "raise", "cut", "billion", "million", "%"]):
                points.append(s.strip() + ".")
            elif any(kw in s.lower() for kw in ["announced", "launched", "acquired", "partnership", "regulatory"]):
                points.append(s.strip() + ".")

        if len(points) < 2:
            points.extend(s.strip() + "." for s in sentences[1:4] if s.strip() not in [p.rstrip(".") for p in points])

        return points[:5]

    def _classify_sentiment(self, article: NewsArticle) -> Dict:
        """Classify article sentiment using stored score or text analysis."""
        if article.sentiment_label and article.sentiment_score:
            return {
                "label": article.sentiment_label,
                "score": float(article.sentiment_score),
                "confidence": 0.85,
                "method": "pre_computed"
            }

        text = (article.title or "") + " " + (article.summary or "")
        text_lower = text.lower()

        positive_signals = sum(1 for w in ["beat", "surge", "growth", "record", "profit", "upgrade", "bullish", "strong", "exceed", "rally"]
                              if w in text_lower)
        negative_signals = sum(1 for w in ["miss", "decline", "loss", "cut", "downgrade", "bearish", "weak", "concern", "risk", "crash"]
                              if w in text_lower)

        net_score = (positive_signals - negative_signals) / max(1, positive_signals + negative_signals)

        if net_score > 0.5:
            label = "very_positive"
        elif net_score > 0.1:
            label = "positive"
        elif net_score < -0.5:
            label = "very_negative"
        elif net_score < -0.1:
            label = "negative"
        else:
            label = "neutral"

        return {
            "label": label,
            "score": round(net_score, 3),
            "confidence": 0.6,
            "method": "keyword_analysis"
        }

    def _assess_market_impact(self, article: NewsArticle, sentiment: Dict) -> Dict:
        """Assess potential market impact."""
        score = abs(sentiment["score"])
        is_breaking = article.is_breaking or False
        relevance = float(article.relevance_score) if article.relevance_score else 0.5

        impact_score = score * 0.5 + relevance * 0.3 + (0.2 if is_breaking else 0)

        if impact_score > 0.7:
            level = "high"
            timeframe = "immediate (intraday)"
        elif impact_score > 0.4:
            level = "moderate"
            timeframe = "short-term (1-3 days)"
        else:
            level = "low"
            timeframe = "minimal or long-term only"

        direction = "positive" if sentiment["score"] > 0 else "negative" if sentiment["score"] < 0 else "neutral"

        return {
            "level": level,
            "direction": direction,
            "impact_score": round(impact_score, 2),
            "timeframe": timeframe,
            "is_breaking": is_breaking
        }

    def _identify_affected_entities(self, article: NewsArticle) -> Dict:
        """Identify companies and sectors affected by this article."""
        companies = []
        sectors = []

        news_companies = self.db.query(NewsCompany).filter(NewsCompany.news_id == article.id).all()
        for nc in news_companies:
            company = self.db.query(Company).filter(Company.id == nc.company_id).first()
            if company:
                companies.append({
                    "id": company.id,
                    "name": company.name,
                    "ticker": company.ticker,
                    "relevance": float(nc.relevance) if nc.relevance else 1.0
                })

        news_sectors = self.db.query(NewsSector).filter(NewsSector.news_id == article.id).all()
        for ns in news_sectors:
            sector = self.db.query(Sector).filter(Sector.id == ns.sector_id).first()
            if sector:
                sectors.append({"id": sector.id, "name": sector.name})

        return {"companies": companies, "sectors": sectors}

    def _generate_recommendation(self, article: NewsArticle, sentiment: Dict, market_impact: Dict) -> Dict:
        """Generate actionable recommendation based on article analysis."""
        if market_impact["level"] == "high" and sentiment["label"] in ("very_negative", "negative"):
            action = "monitor_closely"
            detail = "High-impact negative news. Review exposure to affected companies and consider stop-loss placement."
        elif market_impact["level"] == "high" and sentiment["label"] in ("very_positive", "positive"):
            action = "research_opportunity"
            detail = "Positive catalyst detected. Research the affected companies for potential entry points."
        elif market_impact["level"] == "moderate":
            action = "stay_informed"
            detail = "Monitor developments. This may affect your positions over the next few days."
        else:
            action = "no_action"
            detail = "Low-impact news. No immediate portfolio action recommended."

        return {
            "action": action,
            "detail": detail,
            "urgency": "high" if market_impact["level"] == "high" else "medium" if market_impact["level"] == "moderate" else "low"
        }
