from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.news import NewsArticle, NewsCompany
from app.schemas.alerts import NewsResponse

router = APIRouter()


@router.get("/", response_model=List[NewsResponse])
def list_news(
    company_id: Optional[int] = None,
    category: Optional[str] = None,
    sentiment: Optional[str] = None,
    breaking_only: bool = False,
    limit: int = Query(default=30, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(NewsArticle)

    if company_id:
        query = query.join(NewsCompany).filter(NewsCompany.company_id == company_id)
    if category:
        query = query.filter(NewsArticle.category == category)
    if sentiment:
        query = query.filter(NewsArticle.sentiment_label == sentiment)
    if breaking_only:
        query = query.filter(NewsArticle.is_breaking == True)

    return query.order_by(NewsArticle.published_at.desc()).offset(offset).limit(limit).all()


@router.get("/{news_id}", response_model=NewsResponse)
def get_news_article(news_id: int, db: Session = Depends(get_db)):
    article = db.query(NewsArticle).filter(NewsArticle.id == news_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("/trending/", response_model=List[NewsResponse])
def get_trending_news(
    hours: int = Query(default=24, le=168),
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    return (
        db.query(NewsArticle)
        .filter(NewsArticle.published_at >= cutoff)
        .order_by(NewsArticle.relevance_score.desc().nullslast())
        .limit(limit)
        .all()
    )
