"""
Wrappers for external data provider APIs.
"""
import httpx
from typing import Optional

from app.core.config import get_settings

settings = get_settings()


class AlphaVantageClient:
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY

    async def get_quote(self, ticker: str) -> Optional[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.BASE_URL, params={
                "function": "GLOBAL_QUOTE",
                "symbol": ticker,
                "apikey": self.api_key,
            })
            if resp.status_code == 200:
                data = resp.json()
                return data.get("Global Quote")
            return None

    async def get_daily_prices(self, ticker: str, outputsize: str = "compact") -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.BASE_URL, params={
                "function": "TIME_SERIES_DAILY",
                "symbol": ticker,
                "outputsize": outputsize,
                "apikey": self.api_key,
            })
            if resp.status_code == 200:
                data = resp.json()
                series = data.get("Time Series (Daily)", {})
                return [{"date": k, **v} for k, v in series.items()]
            return []

    async def get_company_overview(self, ticker: str) -> Optional[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.BASE_URL, params={
                "function": "OVERVIEW",
                "symbol": ticker,
                "apikey": self.api_key,
            })
            if resp.status_code == 200:
                return resp.json()
            return None


class PolygonClient:
    BASE_URL = "https://api.polygon.io"

    def __init__(self):
        self.api_key = settings.POLYGON_API_KEY

    async def get_latest_price(self, ticker: str) -> Optional[float]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/v2/last/trade/{ticker}",
                params={"apiKey": self.api_key},
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("results", {}).get("p")
            return None

    async def get_aggregates(self, ticker: str, from_date: str, to_date: str, timespan: str = "day") -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/v2/aggs/ticker/{ticker}/range/1/{timespan}/{from_date}/{to_date}",
                params={"apiKey": self.api_key, "limit": 5000},
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("results", [])
            return []


class FinnhubClient:
    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self):
        self.api_key = settings.FINNHUB_API_KEY

    async def get_quote(self, ticker: str) -> Optional[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.BASE_URL}/quote", params={"symbol": ticker, "token": self.api_key})
            if resp.status_code == 200:
                return resp.json()
            return None

    async def get_news(self, ticker: str, from_date: str, to_date: str) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.BASE_URL}/company-news", params={
                "symbol": ticker, "from": from_date, "to": to_date, "token": self.api_key,
            })
            if resp.status_code == 200:
                return resp.json()
            return []


def get_price_client():
    """Returns the configured price data client."""
    if settings.POLYGON_API_KEY:
        return PolygonClient()
    elif settings.FINNHUB_API_KEY:
        return FinnhubClient()
    return AlphaVantageClient()
