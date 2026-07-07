import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_get_portfolio_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/portfolio")
        assert resp.status_code == 403


@pytest.mark.asyncio
async def test_place_trade_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/portfolio/trades", json={
            "ticker": "AAPL",
            "action": "buy",
            "shares": 10,
        })
        assert resp.status_code == 403
