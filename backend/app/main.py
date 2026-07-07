from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.infrastructure import (
    RateLimitMiddleware,
    CacheMiddleware,
    MonitoringMiddleware,
    metrics
)
from app.routers import auth, users, stocks, portfolio, flags, learning, social, health
from app.routers import companies, alerts, news, watchlists, ai


def create_app() -> FastAPI:
    app = FastAPI(
        title="PreStocks API",
        version="2.0.0",
        description="AI-powered paper trading platform with risk education",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # Middleware stack (order matters: last added = first executed)
    app.add_middleware(MonitoringMiddleware)
    app.add_middleware(CacheMiddleware)
    app.add_middleware(RateLimitMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Core routers
    app.include_router(health.router, tags=["health"])
    app.include_router(auth.router, prefix="/auth", tags=["authentication"])
    app.include_router(users.router, prefix="/users", tags=["users"])

    # Company & Market data
    app.include_router(companies.router, prefix="/companies", tags=["companies"])
    app.include_router(stocks.router, prefix="/stocks", tags=["stocks (legacy)"])
    app.include_router(news.router, prefix="/news", tags=["news"])

    # Portfolio & Trading
    app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
    app.include_router(watchlists.router, prefix="/watchlists", tags=["watchlists"])

    # Risk & Analysis
    app.include_router(flags.router, prefix="/flags", tags=["risk-flags"])

    # AI & Intelligence
    app.include_router(ai.router, prefix="/ai", tags=["ai-engine"])

    # Social & Learning
    app.include_router(learning.router, prefix="/learning", tags=["learning"])
    app.include_router(social.router, prefix="/social", tags=["social"])

    # Alerts & Notifications
    app.include_router(alerts.router, prefix="/notifications", tags=["notifications"])

    # Internal/Admin endpoints
    @app.get("/metrics", tags=["admin"])
    def get_metrics():
        return metrics.get_summary()

    @app.get("/", tags=["root"])
    def root():
        return {
            "name": "PreStocks API",
            "version": "2.0.0",
            "status": "operational",
            "docs": "/docs" if settings.DEBUG else None,
            "endpoints": {
                "auth": "/auth",
                "companies": "/companies",
                "portfolio": "/portfolio",
                "watchlists": "/watchlists",
                "ai_research": "/ai/research",
                "ai_portfolio_advice": "/ai/portfolio-advice",
                "ai_chat": "/ai/chat",
                "news": "/news",
                "notifications": "/notifications",
                "risk_flags": "/flags",
                "learning": "/learning",
                "social": "/social",
                "metrics": "/metrics"
            }
        }

    return app


app = create_app()
