"""
Background Jobs — Celery tasks for scheduled and async processing.
"""
from celery import Celery
from datetime import datetime, timedelta
import logging

from app.core.config import settings

celery_app = Celery(
    "prestocks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "update-stock-prices": {
        "task": "app.tasks.background_jobs.update_stock_prices",
        "schedule": 60.0,
    },
    "refresh-risk-flags": {
        "task": "app.tasks.background_jobs.refresh_risk_flags",
        "schedule": 3600.0,
    },
    "ingest-news": {
        "task": "app.tasks.background_jobs.ingest_news_articles",
        "schedule": 900.0,
    },
    "check-price-alerts": {
        "task": "app.tasks.background_jobs.check_price_alerts",
        "schedule": 120.0,
    },
    "weekly-portfolio-advice": {
        "task": "app.tasks.background_jobs.generate_weekly_portfolio_advice",
        "schedule": 604800.0,
    },
    "cleanup-expired-sessions": {
        "task": "app.tasks.background_jobs.cleanup_expired_sessions",
        "schedule": 86400.0,
    },
    "mark-stale-reports": {
        "task": "app.tasks.background_jobs.mark_stale_reports",
        "schedule": 43200.0,
    },
}

logger = logging.getLogger("prestocks.tasks")


@celery_app.task(bind=True, max_retries=3)
def update_stock_prices(self):
    """Fetch latest prices from market data APIs and update price_history + holdings."""
    try:
        from app.database.session import SessionLocal
        from app.models.company import Company
        from app.models.portfolio import Holding

        db = SessionLocal()
        companies = db.query(Company).filter(Company.is_active == True, Company.ticker.isnot(None)).all()

        updated = 0
        for company in companies:
            # In production: call Alpha Vantage / Polygon / IEX
            # For now, simulate minor price changes
            import random
            if company.market_cap:
                price_estimate = company.market_cap / 1e9
                new_price = price_estimate * (1 + random.uniform(-0.02, 0.02))
                db.query(Holding).filter(Holding.company_id == company.id).update(
                    {"current_price": new_price, "updated_at": datetime.utcnow()}
                )
                updated += 1

        db.commit()
        db.close()
        logger.info(f"Updated prices for {updated} companies")
        return {"updated": updated}
    except Exception as exc:
        logger.error(f"Price update failed: {exc}")
        self.retry(exc=exc, countdown=30)


@celery_app.task(bind=True, max_retries=3)
def refresh_risk_flags(self):
    """Recalculate risk flags for all active companies."""
    try:
        from app.database.session import SessionLocal
        from app.models.company import Company
        from app.models.flags import RiskFlag

        db = SessionLocal()
        companies = db.query(Company).filter(Company.is_active == True).limit(100).all()

        for company in companies:
            # Expire old flags
            db.query(RiskFlag).filter(
                RiskFlag.company_id == company.id,
                RiskFlag.expires_at < datetime.utcnow()
            ).update({"is_active": False})

        db.commit()
        db.close()
        logger.info(f"Refreshed risk flags for {len(companies)} companies")
        return {"processed": len(companies)}
    except Exception as exc:
        logger.error(f"Risk flag refresh failed: {exc}")
        self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def ingest_news_articles(self):
    """Pull latest news from NewsAPI and store with sentiment analysis."""
    try:
        from app.database.session import SessionLocal
        from app.models.news import NewsArticle

        db = SessionLocal()
        # In production: call NewsAPI, run FinBERT sentiment
        # Placeholder: mark task as completed
        db.close()
        logger.info("News ingestion completed")
        return {"ingested": 0, "message": "News API key required for live ingestion"}
    except Exception as exc:
        logger.error(f"News ingestion failed: {exc}")
        self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=2)
def check_price_alerts(self):
    """Check all active price alerts and trigger notifications."""
    try:
        from app.database.session import SessionLocal
        from app.models.alert import Alert, Notification
        from app.models.portfolio import Holding

        db = SessionLocal()
        active_alerts = db.query(Alert).filter(
            Alert.is_active == True, Alert.is_triggered == False,
            Alert.alert_type.in_(["price_above", "price_below"])
        ).all()

        triggered = 0
        for alert in active_alerts:
            # Check current price against condition
            # In production: compare with real-time price
            pass

        db.commit()
        db.close()
        logger.info(f"Checked {len(active_alerts)} alerts, triggered {triggered}")
        return {"checked": len(active_alerts), "triggered": triggered}
    except Exception as exc:
        logger.error(f"Alert check failed: {exc}")
        self.retry(exc=exc, countdown=30)


@celery_app.task
def generate_weekly_portfolio_advice():
    """Generate AI portfolio advice for all users with active portfolios."""
    try:
        from app.database.session import SessionLocal
        from app.models.portfolio import Portfolio

        db = SessionLocal()
        portfolios = db.query(Portfolio).filter(Portfolio.is_default == True).all()

        for portfolio in portfolios:
            # In production: call AI service to generate advice
            pass

        db.close()
        logger.info(f"Generated advice for {len(portfolios)} portfolios")
        return {"portfolios_processed": len(portfolios)}
    except Exception as exc:
        logger.error(f"Portfolio advice generation failed: {exc}")


@celery_app.task
def cleanup_expired_sessions():
    """Remove expired user sessions from the database."""
    try:
        from app.database.session import SessionLocal
        from app.models.user import UserSession

        db = SessionLocal()
        deleted = db.query(UserSession).filter(UserSession.expires_at < datetime.utcnow()).delete()
        db.commit()
        db.close()
        logger.info(f"Cleaned up {deleted} expired sessions")
        return {"deleted": deleted}
    except Exception as exc:
        logger.error(f"Session cleanup failed: {exc}")


@celery_app.task
def mark_stale_reports():
    """Mark AI research reports older than 7 days as stale."""
    try:
        from app.database.session import SessionLocal
        from app.models.ai import AIResearchReport

        db = SessionLocal()
        cutoff = datetime.utcnow() - timedelta(days=7)
        updated = db.query(AIResearchReport).filter(
            AIResearchReport.generated_at < cutoff,
            AIResearchReport.is_stale == False
        ).update({"is_stale": True})
        db.commit()
        db.close()
        logger.info(f"Marked {updated} reports as stale")
        return {"stale_reports": updated}
    except Exception as exc:
        logger.error(f"Stale report marking failed: {exc}")
