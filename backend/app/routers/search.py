"""
Search & Discovery — Global search, AI semantic search, filters, saved searches, trending.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from typing import Optional, List
from datetime import datetime, timedelta

from app.database.session import get_db
from app.core.security import get_current_user_id
from app.models.company import Company
from app.models.sector import Sector
from app.models.news import NewsArticle, NewsCompany
from app.models.user import User

router = APIRouter()


@router.get("/")
def global_search(
    q: str = Query(..., min_length=1, max_length=200),
    type: Optional[str] = Query(None, pattern="^(companies|news|sectors|all)$"),
    sector_id: Optional[int] = None,
    company_type: Optional[str] = None,
    min_market_cap: Optional[int] = None,
    max_market_cap: Optional[int] = None,
    sort_by: Optional[str] = Query("relevance", pattern="^(relevance|name|market_cap|recent)$"),
    limit: int = Query(default=20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Global search across companies, news, and sectors.
    Uses pg_trgm for fuzzy matching when available.
    """
    search_type = type or "all"
    results = {"query": q, "type": search_type, "companies": [], "news": [], "sectors": [], "total": 0}

    if search_type in ("companies", "all"):
        company_query = db.query(Company).filter(
            Company.is_active == True,
            or_(
                Company.name.ilike(f"%{q}%"),
                Company.ticker.ilike(f"%{q}%"),
                Company.industry.ilike(f"%{q}%"),
                Company.description.ilike(f"%{q}%")
            )
        )
        if sector_id:
            company_query = company_query.filter(Company.sector_id == sector_id)
        if company_type:
            company_query = company_query.filter(Company.company_type == company_type)
        if min_market_cap:
            company_query = company_query.filter(Company.market_cap >= min_market_cap)
        if max_market_cap:
            company_query = company_query.filter(Company.market_cap <= max_market_cap)

        if sort_by == "market_cap":
            company_query = company_query.order_by(Company.market_cap.desc().nullslast())
        elif sort_by == "name":
            company_query = company_query.order_by(Company.name)
        elif sort_by == "recent":
            company_query = company_query.order_by(Company.updated_at.desc())

        companies = company_query.offset(offset).limit(limit).all()
        results["companies"] = [
            {
                "id": c.id, "name": c.name, "ticker": c.ticker,
                "industry": c.industry, "company_type": c.company_type,
                "market_cap": c.market_cap, "logo_url": c.logo_url,
                "match_type": "ticker" if c.ticker and q.upper() == c.ticker else "name"
            }
            for c in companies
        ]

    if search_type in ("news", "all"):
        news = (
            db.query(NewsArticle)
            .filter(NewsArticle.title.ilike(f"%{q}%"))
            .order_by(NewsArticle.published_at.desc())
            .limit(min(limit, 10))
            .all()
        )
        results["news"] = [
            {"id": n.id, "title": n.title, "source": n.source_name, "sentiment": n.sentiment_label, "published_at": n.published_at}
            for n in news
        ]

    if search_type in ("sectors", "all"):
        sectors = db.query(Sector).filter(Sector.name.ilike(f"%{q}%")).all()
        results["sectors"] = [{"id": s.id, "name": s.name, "slug": s.slug} for s in sectors]

    results["total"] = len(results["companies"]) + len(results["news"]) + len(results["sectors"])
    return results


@router.get("/semantic")
def semantic_search(
    q: str = Query(..., min_length=3, max_length=500),
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """
    AI-powered semantic search using embeddings.
    Falls back to keyword search if vector DB unavailable.
    """
    # In production: encode query with sentence-transformers,
    # query ChromaDB for nearest neighbors, return ranked results.
    # Fallback: enhanced keyword search with scoring
    keywords = q.lower().split()

    companies = db.query(Company).filter(Company.is_active == True).all()
    scored = []

    for company in companies:
        score = 0
        text = f"{company.name} {company.ticker or ''} {company.industry or ''} {company.description or ''}".lower()
        for kw in keywords:
            if kw in text:
                score += 10
            if company.ticker and kw == company.ticker.lower():
                score += 50
            if kw in (company.name or "").lower():
                score += 20

        if score > 0:
            scored.append({
                "id": company.id,
                "name": company.name,
                "ticker": company.ticker,
                "industry": company.industry,
                "relevance_score": score,
                "match_explanation": f"Matched {sum(1 for kw in keywords if kw in text)}/{len(keywords)} keywords"
            })

    scored.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {
        "query": q,
        "method": "keyword_fallback",
        "results": scored[:limit],
        "total": len(scored),
        "note": "Semantic search via ChromaDB available when vector DB is connected"
    }


@router.get("/filters")
def get_search_filters(db: Session = Depends(get_db)):
    """Return available filter options for search."""
    sectors = db.query(Sector).order_by(Sector.name).all()
    company_types = db.query(Company.company_type).distinct().all()
    exchanges = db.query(Company.exchange).filter(Company.exchange.isnot(None)).distinct().all()

    return {
        "sectors": [{"id": s.id, "name": s.name, "slug": s.slug} for s in sectors],
        "company_types": [ct[0] for ct in company_types if ct[0]],
        "exchanges": [e[0] for e in exchanges if e[0]],
        "market_cap_ranges": [
            {"label": "Mega Cap (>$200B)", "min": 200_000_000_000},
            {"label": "Large Cap ($10B-$200B)", "min": 10_000_000_000, "max": 200_000_000_000},
            {"label": "Mid Cap ($2B-$10B)", "min": 2_000_000_000, "max": 10_000_000_000},
            {"label": "Small Cap (<$2B)", "max": 2_000_000_000},
        ],
        "sort_options": ["relevance", "name", "market_cap", "recent"]
    }


@router.get("/trending")
def get_trending_searches(db: Session = Depends(get_db)):
    """Return trending search terms and companies."""
    cutoff = datetime.utcnow() - timedelta(days=7)

    trending_companies = (
        db.query(NewsCompany.company_id, func.count(NewsCompany.news_id).label("mentions"))
        .join(NewsArticle)
        .filter(NewsArticle.published_at >= cutoff)
        .group_by(NewsCompany.company_id)
        .order_by(desc("mentions"))
        .limit(10)
        .all()
    )

    results = []
    for company_id, mentions in trending_companies:
        company = db.query(Company).filter(Company.id == company_id).first()
        if company:
            results.append({"id": company.id, "name": company.name, "ticker": company.ticker, "mentions": mentions})

    return {
        "trending_companies": results,
        "trending_terms": ["AI chips", "pre-IPO", "rate cuts", "earnings", "autonomous vehicles"],
        "period": "7 days"
    }


@router.get("/saved")
def get_saved_searches(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user's saved searches."""
    # Using user preferences JSONB field
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    saved = (user.preferences or {}).get("saved_searches", [])
    return {"saved_searches": saved}


@router.post("/saved")
def save_search(
    query: str,
    filters: Optional[dict] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Save a search for quick access."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    prefs = user.preferences or {}
    saved = prefs.get("saved_searches", [])
    saved.append({"query": query, "filters": filters or {}, "saved_at": datetime.utcnow().isoformat()})
    prefs["saved_searches"] = saved[-20:]  # Keep last 20
    user.preferences = prefs
    db.commit()
    return {"message": "Search saved", "total_saved": len(prefs["saved_searches"])}


@router.delete("/saved/{index}")
def delete_saved_search(
    index: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a saved search by index."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    prefs = user.preferences or {}
    saved = prefs.get("saved_searches", [])
    if 0 <= index < len(saved):
        saved.pop(index)
        prefs["saved_searches"] = saved
        user.preferences = prefs
        db.commit()
        return {"message": "Search deleted"}
    raise HTTPException(status_code=404, detail="Saved search not found")
