from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "prestocks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.update_prices",
        "app.tasks.calculate_flags",
        "app.tasks.ingest_news",
        "app.tasks.ingest_insider_filings",
        "app.tasks.background_jobs",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

celery_app.conf.beat_schedule = {
    "check-price-alerts-every-5min": {
        "task": "tasks.check_price_alerts",
        "schedule": crontab(minute="*/5"),
    },
    "refresh-risk-flags-every-hour": {
        "task": "tasks.refresh_risk_flags",
        "schedule": crontab(minute=0),
    },
    "ingest-news-every-30min": {
        "task": "tasks.ingest_news_articles",
        "schedule": crontab(minute="*/30"),
    },
    "weekly-portfolio-advice-monday-9am": {
        "task": "tasks.generate_weekly_portfolio_advice",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),
    },
    "mark-stale-reports-daily": {
        "task": "tasks.mark_stale_reports",
        "schedule": crontab(hour=3, minute=0),
    },
    "cleanup-sessions-daily": {
        "task": "tasks.cleanup_expired_sessions",
        "schedule": crontab(hour=4, minute=0),
    },
}
