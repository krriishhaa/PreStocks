from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import time

from app.database import get_db
from app.core.security import get_current_user_id
from app.schemas.ai import (
    AIResearchRequest, AIResearchResponse,
    PortfolioAdviceRequest, PortfolioAdviceResponse,
    AIChatRequest, AIChatResponse
)
from app.services.ai_research_engine import AIResearchEngine
from app.services.ai_portfolio_advisor import AIPortfolioAdvisor

router = APIRouter()


@router.post("/research", response_model=AIResearchResponse)
def analyze_company(
    payload: AIResearchRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    engine = AIResearchEngine(db)
    start = time.time()

    report = engine.generate_research_report(
        user_id=user_id,
        company_id=payload.company_id,
        ticker=payload.ticker,
        company_name=payload.company_name,
        report_type=payload.report_type,
        include_sections=payload.include_sections
    )

    elapsed_ms = int((time.time() - start) * 1000)
    report.generation_time_ms = elapsed_ms
    db.commit()
    db.refresh(report)
    return report


@router.get("/research/{company_id}", response_model=AIResearchResponse)
def get_latest_research(
    company_id: int,
    report_type: str = "full_analysis",
    db: Session = Depends(get_db)
):
    from app.models.ai import AIResearchReport
    report = (
        db.query(AIResearchReport)
        .filter(
            AIResearchReport.company_id == company_id,
            AIResearchReport.report_type == report_type,
            AIResearchReport.is_stale == False
        )
        .order_by(AIResearchReport.created_at.desc())
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="No research report found. Generate one first.")
    return report


@router.post("/portfolio-advice", response_model=PortfolioAdviceResponse)
def get_portfolio_advice(
    payload: PortfolioAdviceRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    advisor = AIPortfolioAdvisor(db)
    advice = advisor.generate_advice(
        user_id=user_id,
        portfolio_id=payload.portfolio_id,
        advice_type=payload.advice_type
    )
    return advice


@router.get("/portfolio-advice/latest", response_model=PortfolioAdviceResponse)
def get_latest_portfolio_advice(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    from app.models.ai import AIPortfolioAdvice
    advice = (
        db.query(AIPortfolioAdvice)
        .filter(AIPortfolioAdvice.user_id == user_id)
        .order_by(AIPortfolioAdvice.created_at.desc())
        .first()
    )
    if not advice:
        raise HTTPException(status_code=404, detail="No portfolio advice yet. Request one first.")
    return advice


@router.post("/chat", response_model=AIChatResponse)
def ai_chat(
    payload: AIChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    from app.services.ai_chat_service import AIChatService
    service = AIChatService(db)
    return service.process_message(
        user_id=user_id,
        message=payload.message,
        conversation_id=payload.conversation_id,
        company_id=payload.company_id,
        context_type=payload.context_type
    )


@router.get("/conversations")
def list_conversations(
    limit: int = 20,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    from app.models.ai import AIConversation
    return (
        db.query(AIConversation)
        .filter(AIConversation.user_id == user_id)
        .order_by(AIConversation.updated_at.desc())
        .limit(limit)
        .all()
    )


# ─── News Summarization ───

@router.get("/news/summarize/{article_id}")
def summarize_article(article_id: int, db: Session = Depends(get_db)):
    from app.services.ai_news_summarizer import AINewsSummarizer
    summarizer = AINewsSummarizer(db)
    return summarizer.summarize_article(article_id)


@router.get("/news/summarize/company/{company_id}")
def summarize_company_news(
    company_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    from app.services.ai_news_summarizer import AINewsSummarizer
    summarizer = AINewsSummarizer(db)
    return summarizer.summarize_for_company(company_id, limit)


@router.get("/news/digest")
def get_market_digest(
    hours: int = 24,
    limit: int = 15,
    db: Session = Depends(get_db)
):
    """Get AI-generated market news digest with sentiment and impact analysis."""
    from app.services.ai_news_summarizer import AINewsSummarizer
    summarizer = AINewsSummarizer(db)
    return summarizer.get_market_digest(hours, limit)


# ─── Recommendation Engine ───

@router.get("/recommendations")
def get_recommendations(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get full personalized recommendations: companies, sectors, watchlists."""
    from app.services.recommendation_engine import RecommendationEngine
    engine = RecommendationEngine(db)
    return engine.get_recommendations(user_id)


@router.get("/recommendations/companies")
def get_company_recommendations(
    limit: int = 10,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get personalized company recommendations."""
    from app.services.recommendation_engine import RecommendationEngine
    engine = RecommendationEngine(db)
    return engine.recommend_companies(user_id, limit)


@router.get("/recommendations/sectors")
def get_sector_recommendations(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get sector diversification recommendations."""
    from app.services.recommendation_engine import RecommendationEngine
    engine = RecommendationEngine(db)
    return engine.recommend_sectors(user_id)


@router.get("/recommendations/watchlists")
def get_watchlist_recommendations(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get curated watchlist suggestions based on user tier."""
    from app.services.recommendation_engine import RecommendationEngine
    engine = RecommendationEngine(db)
    return engine.recommend_watchlists(user_id)
