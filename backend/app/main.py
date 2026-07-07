"""
PreStocks API — Minimal working application (real auth + portfolio + learning).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, portfolio, learning

app = FastAPI(
    title="PreStocks API",
    version="1.0.0",
    description="Paper trading platform — real auth, portfolio, and learning progress.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
app.include_router(learning.router, prefix="/learning", tags=["learning"])


@app.get("/")
def root():
    return {"name": "PreStocks API", "version": "1.0.0", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}
