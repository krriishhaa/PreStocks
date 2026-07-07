"""
PreStocks API — Main Application Factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.infrastructure import (
    RateLimitMiddleware,
    CacheMiddleware,
    MonitoringMiddleware,
    metrics,
    response_cache
)
from app.routers import (
    auth, users, stocks, portfolio, flags,
    learning, social, health, companies,
    news, watchlists, ai, notifications
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="PreStocks API",
        version="3.0.0",
        description="AI-powered paper trading platform with comprehensive risk education, "
                    "pre-IPO research, and portfolio management.",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # Middleware (last added = first executed)
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

    # ─── Core ───
    app.include_router(health.router, tags=["health"])
    app.include_router(auth.router, prefix="/auth", tags=["authentication"])
    app.include_router(users.router, prefix="/users", tags=["users"])

    # ─── Companies & Market Data ───
    app.include_router(companies.router, prefix="/companies", tags=["companies"])
    app.include_router(stocks.router, prefix="/stocks", tags=["stocks-legacy"])
    app.include_router(news.router, prefix="/news", tags=["news"])

    # ─── Portfolio & Trading ───
    app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
    app.include_router(watchlists.router, prefix="/watchlists", tags=["watchlists"])

    # ─── Risk Analysis ───
    app.include_router(flags.router, prefix="/flags", tags=["risk-flags"])

    # ─── AI & Intelligence ───
    app.include_router(ai.router, prefix="/ai", tags=["ai-engine"])

    # ─── Social & Learning ───
    app.include_router(learning.router, prefix="/learning", tags=["learning"])
    app.include_router(social.router, prefix="/social", tags=["social"])

    # ─── Notifications & Alerts ───
    app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

    # ─── Admin/Internal ───
    @app.get("/metrics", tags=["admin"])
    def get_metrics():
        return metrics.get_summary()

    @app.get("/cache/stats", tags=["admin"])
    def cache_stats():
        return response_cache.stats()

    @app.post("/cache/invalidate", tags=["admin"])
    def invalidate_cache(pattern: str = ""):
        response_cache.invalidate(pattern)
        return {"message": f"Cache invalidated for pattern: '{pattern}'"}

    @app.get("/", tags=["root"])
    def root():
        return {
            "name": "PreStocks API",
            "version": "3.0.0",
            "status": "operational",
            "docs": "/docs" if settings.DEBUG else None,
            "endpoints": {
                "auth": {"signup": "POST /auth/signup", "login": "POST /auth/login", "refresh": "POST /auth/refresh", "me": "GET /auth/me"},
                "companies": {"search": "GET /companies/search?q=", "detail": "GET /companies/{id}", "fundamentals": "GET /companies/{id}/fundamentals", "funding": "GET /companies/{id}/funding-rounds", "competitors": "GET /companies/{id}/competitors", "risk_flags": "GET /companies/{id}/risk-flags"},
                "portfolio": {"get": "GET /portfolio", "summary": "GET /portfolio/summary", "trade": "POST /portfolio/trades", "history": "GET /portfolio/trades", "risk": "GET /portfolio/risk-summary"},
                "watchlists": {"list": "GET /watchlists/", "create": "POST /watchlists/", "items": "GET /watchlists/{id}/items", "add_item": "POST /watchlists/{id}/items"},
                "ai": {"research": "POST /ai/research", "portfolio_advice": "POST /ai/portfolio-advice", "chat": "POST /ai/chat"},
                "news": {"list": "GET /news/", "trending": "GET /news/trending/", "detail": "GET /news/{id}"},
                "notifications": {"list": "GET /notifications/", "unread": "GET /notifications/unread-count", "alerts": "GET /notifications/alerts"},
                "risk_flags": "GET /flags/",
                "learning": "GET /learning/modules",
                "social": "GET /social/feed",
                "metrics": "GET /metrics"
            }
        }

    return app


app = create_app()
