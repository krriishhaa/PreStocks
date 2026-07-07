import os
from dataclasses import dataclass


@dataclass(frozen=True)
class InfraSettings:
    postgres_url: str = os.getenv(
        "POSTGRES_URL",
        "sqlite:///backend/prestocks_infra.db",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    default_history_days: int = int(os.getenv("INFRA_HISTORY_DAYS", "90"))
    max_news_items_per_source: int = int(os.getenv("INFRA_NEWS_LIMIT", "50"))
    pipeline_max_attempts: int = int(os.getenv("INFRA_PIPELINE_MAX_ATTEMPTS", "3"))
    pipeline_backoff_seconds: int = int(os.getenv("INFRA_PIPELINE_BACKOFF_SECONDS", "2"))
    app_env: str = os.getenv("APP_ENV", "development")
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "")
    fred_api_key: str = os.getenv("FRED_API_KEY", "")
    sec_user_agent: str = os.getenv(
        "SEC_USER_AGENT",
        "PreStocksDataInfra/1.2 admin@prestocks.local",
    )
    slack_webhook_url: str = os.getenv("SLACK_WEBHOOK_URL", "")
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "infra-alerts@prestocks.local")
    alert_to_email: str = os.getenv("ALERT_TO_EMAIL", "")


SETTINGS = InfraSettings()

