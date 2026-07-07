"""
Background Jobs — Celery tasks for async processing.
"""

from celery import shared_task
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("prestocks.tasks")


@shared_task(name="tasks.generate_weekly_portfolio_advice")
def generate_weekly_portfolio_advice():
    """Run weekly portfolio analysis for all active users."""
    from app.database.session import SessionLocal
    from app.models.user import User
    from app.models.portfolio import Portfolio
    from app.services.ai_portfolio_advisor import AIPortfolioAdvisor

    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        for user in users:
            portfolio = db.query(Portfolio).filter(
                Portfolio.user_id == user.id, Portfolio.is_default == True
            ).first()
            if not portfolio:
                continue

            advisor = AIPortfolioAdvisor(db)
            try:
                advisor.generate_advice(
                    user_id=user.id,
                    portfolio_id=portfolio.id,
                    advice_type="weekly_review"
                )
                logger.info(f"Generated weekly advice for user {user.id}")
            except Exception as e:
                logger.error(f"Failed generating advice for user {user.id}: {e}")
    finally:
        db.close()


@shared_task(name="tasks.check_price_alerts")
def check_price_alerts():
    """Check all active price alerts against current prices."""
    from app.database.session import SessionLocal
    from app.models.alert import Alert, Notification
    from app.models.company import Company

    db = SessionLocal()
    try:
        active_alerts = db.query(Alert).filter(
            Alert.is_active == True,
            Alert.alert_type.in_(["price_above", "price_below"])
        ).all()

        for alert in active_alerts:
            if alert.last_notified_at:
                cooldown_until = alert.last_notified_at + timedelta(hours=alert.cooldown_hours)
                if datetime.utcnow() < cooldown_until:
                    continue

            company = db.query(Company).filter(Company.id == alert.company_id).first()
            if not company or not company.market_cap:
                continue

            condition = alert.condition or {}
            threshold = condition.get("price")
            if not threshold:
                continue

            triggered = False
            if alert.alert_type == "price_above" and company.market_cap > threshold:
                triggered = True
            elif alert.alert_type == "price_below" and company.market_cap < threshold:
                triggered = True

            if triggered:
                alert.is_triggered = True
                alert.triggered_at = datetime.utcnow()
                alert.last_notified_at = datetime.utcnow()

                notification = Notification(
                    user_id=alert.user_id,
                    alert_id=alert.id,
                    type="price_alert",
                    title=alert.title or f"Price Alert: {company.ticker}",
                    message=alert.message or f"{company.ticker} has hit your target price.",
                    channel="in_app"
                )
                db.add(notification)

        db.commit()
    finally:
        db.close()


@shared_task(name="tasks.refresh_risk_flags")
def refresh_risk_flags():
    """Recalculate risk flags for all tracked companies."""
    from app.database.session import SessionLocal
    from app.models.company import Company
    from app.services.flag_calculation_engine import FlagCalculationEngine

    db = SessionLocal()
    try:
        companies = db.query(Company).filter(Company.is_active == True).limit(100).all()
        engine = FlagCalculationEngine(db)

        for company in companies:
            try:
                engine.calculate_all_flags(company.id)
            except Exception as e:
                logger.error(f"Flag calculation failed for {company.ticker}: {e}")

        db.commit()
        logger.info(f"Refreshed risk flags for {len(companies)} companies")
    finally:
        db.close()


@shared_task(name="tasks.ingest_news_articles")
def ingest_news_articles():
    """Fetch latest news from configured sources."""
    from app.database.session import SessionLocal
    from app.models.news import NewsArticle
    logger.info("News ingestion task triggered")
    # Implementation depends on configured news API
    pass


@shared_task(name="tasks.mark_stale_reports")
def mark_stale_reports():
    """Mark AI research reports older than their valid_until date as stale."""
    from app.database.session import SessionLocal
    from app.models.ai import AIResearchReport

    db = SessionLocal()
    try:
        stale = db.query(AIResearchReport).filter(
            AIResearchReport.valid_until < datetime.utcnow(),
            AIResearchReport.is_stale == False
        ).all()

        for report in stale:
            report.is_stale = True

        db.commit()
        logger.info(f"Marked {len(stale)} reports as stale")
    finally:
        db.close()


@shared_task(name="tasks.cleanup_expired_sessions")
def cleanup_expired_sessions():
    """Remove expired user sessions."""
    from app.database.session import SessionLocal
    from app.models.user import User
    from sqlalchemy import text

    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM user_session WHERE expires_at < NOW()"))
        db.commit()
        logger.info("Cleaned up expired sessions")
    finally:
        db.close()
