"""
Celery application configuration with beat schedule.
"""
from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "prestocks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="US/Eastern",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Beat schedule — automated recurring tasks
celery_app.conf.beat_schedule = {
    "update-prices-every-minute": {
        "task": "tasks.update_prices",
        "schedule": 60.0,  # every 60 seconds
        "options": {"queue": "prices"},
    },
    "calculate-flags-every-5-minutes": {
        "task": "tasks.calculate_flags",
        "schedule": 300.0,  # every 5 minutes
        "options": {"queue": "flags"},
    },
    "ingest-news-hourly": {
        "task": "tasks.ingest_news",
        "schedule": 3600.0,  # every hour
        "options": {"queue": "data"},
    },
    "ingest-insider-filings-daily": {
        "task": "tasks.ingest_insider_filings",
        "schedule": crontab(hour=18, minute=0),  # 6 PM ET (after market close)
        "options": {"queue": "data"},
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
