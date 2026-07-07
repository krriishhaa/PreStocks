from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/prestocks_dev"

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 7

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # App settings
    DEBUG: bool = True
    APP_NAME: str = "PreStocks API"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://krriishhaa.github.io"
    ]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_AI_PER_MINUTE: int = 20
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10

    # Caching
    CACHE_TTL_DEFAULT: int = 60
    CACHE_TTL_COMPANIES: int = 300
    CACHE_TTL_NEWS: int = 120
    CACHE_MAX_SIZE: int = 2000

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # External Data APIs
    ALPHA_VANTAGE_API_KEY: str = ""
    POLYGON_API_KEY: str = ""
    FINNHUB_API_KEY: str = ""
    IEX_CLOUD_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    SEC_EDGAR_USER_AGENT: str = "PreStocks research@prestocks.com"

    # AI/ML
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    AI_MODEL_DEFAULT: str = "claude-sonnet-4-20250514"
    AI_MAX_TOKENS: int = 4000
    AI_TEMPERATURE: float = 0.3

    # Vector DB
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8000

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"
    SLOW_REQUEST_THRESHOLD_MS: int = 5000

    # Feature Flags
    ENABLE_AI_CHAT: bool = True
    ENABLE_SOCIAL_FEATURES: bool = True
    ENABLE_PAPER_TRADING: bool = True
    MAX_PAPER_CAPITAL: float = 100000.00
    DEFAULT_PAPER_CAPITAL: float = 10000.00

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
