import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_get_flags_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/flags/stock/AAPL")
        assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_composite_score_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/flags/stock/AAPL/score")
        assert resp.status_code == 403
