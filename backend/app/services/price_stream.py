"""
Real-time price update stream via WebSocket (Finnhub).
Connects to market data feed, updates Redis cache,
and triggers flag recalculation on significant moves.
"""
import json
import asyncio
from typing import Optional

import websockets
import httpx

from app.core.config import get_settings
from app.utils.redis_cache import RedisCache
from app.utils.logger import logger

settings = get_settings()

PRICE_MOVE_THRESHOLD = 0.02  # 2% move triggers flag recalculation


class PriceStreamManager:
    """Manages WebSocket connection to market data provider."""

    def __init__(self):
        self.cache = RedisCache()
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.subscribed_tickers: set[str] = set()
        self._running = False

    async def start(self, tickers: list[str]):
        """Start the WebSocket price stream for given tickers."""
        self._running = True
        self.subscribed_tickers = set(tickers)

        ws_url = f"wss://ws.finnhub.io?token={settings.FINNHUB_API_KEY}"

        while self._running:
            try:
                async with websockets.connect(ws_url) as ws:
                    self.ws = ws
                    logger.info(f"Connected to Finnhub WebSocket. Subscribing to {len(tickers)} tickers.")

                    # Subscribe to tickers
                    for ticker in tickers:
                        await ws.send(json.dumps({"type": "subscribe", "symbol": ticker}))

                    # Process incoming messages
                    async for message in ws:
                        if not self._running:
                            break
                        await self._process_message(message)

            except websockets.ConnectionClosed:
                logger.warning("WebSocket connection closed. Reconnecting in 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"WebSocket error: {e}. Reconnecting in 10s...")
                await asyncio.sleep(10)

    async def stop(self):
        """Gracefully stop the price stream."""
        self._running = False
        if self.ws:
            for ticker in self.subscribed_tickers:
                await self.ws.send(json.dumps({"type": "unsubscribe", "symbol": ticker}))
            await self.ws.close()

    async def _process_message(self, raw_message: str):
        """Process incoming WebSocket message and update cache."""
        try:
            data = json.loads(raw_message)

            if data.get("type") != "trade":
                return

            for tick_data in data.get("data", []):
                ticker = tick_data.get("s", "")
                price = tick_data.get("p", 0)
                volume = tick_data.get("v", 0)
                timestamp = tick_data.get("t", 0)

                if not ticker or not price:
                    continue

                # Update Redis cache
                await self.cache.set_price(ticker, price)

                # Check for significant price move
                old_price_str = await self.cache.get(f"price:{ticker}:prev")
                if old_price_str:
                    old_price = float(old_price_str)
                    if old_price > 0:
                        move_pct = abs((price - old_price) / old_price)
                        if move_pct > PRICE_MOVE_THRESHOLD:
                            logger.info(f"{ticker} moved {move_pct*100:.1f}% — triggering flag recalculation")
                            await self._trigger_flag_recalculation(ticker)

                # Store previous price for next comparison
                await self.cache.set(f"price:{ticker}:prev", str(price), ex=300)

        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.error(f"Error processing price message: {e}")

    async def _trigger_flag_recalculation(self, ticker: str):
        """Queue a flag recalculation task for the ticker."""
        # In production with Celery:
        # from app.tasks.calculate_flags import recalculate_single_ticker
        # recalculate_single_ticker.delay(ticker)

        # For now, just mark in cache that recalculation is needed
        await self.cache.set(f"flag_recalc_needed:{ticker}", "1", ex=300)


class PriceFetcher:
    """Fallback HTTP-based price fetcher when WebSocket is unavailable."""

    def __init__(self):
        self.cache = RedisCache()

    async def fetch_batch_prices(self, tickers: list[str]) -> dict[str, float]:
        """Fetch latest prices for multiple tickers via REST API."""
        prices = {}

        for ticker in tickers:
            # Try cache first
            cached = await self.cache.get_price(ticker)
            if cached is not None:
                prices[ticker] = cached
                continue

            # Fetch from API
            price = await self._fetch_single_price(ticker)
            if price:
                prices[ticker] = price
                await self.cache.set_price(ticker, price)

        return prices

    async def _fetch_single_price(self, ticker: str) -> Optional[float]:
        """Fetch a single ticker price from the configured data provider."""
        if settings.FINNHUB_API_KEY:
            return await self._fetch_finnhub(ticker)
        elif settings.ALPHA_VANTAGE_API_KEY:
            return await self._fetch_alpha_vantage(ticker)
        return None

    async def _fetch_finnhub(self, ticker: str) -> Optional[float]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://finnhub.io/api/v1/quote",
                params={"symbol": ticker, "token": settings.FINNHUB_API_KEY},
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("c")  # current price
        return None

    async def _fetch_alpha_vantage(self, ticker: str) -> Optional[float]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "GLOBAL_QUOTE",
                    "symbol": ticker,
                    "apikey": settings.ALPHA_VANTAGE_API_KEY,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                quote = data.get("Global Quote", {})
                price_str = quote.get("05. price")
                if price_str:
                    return float(price_str)
        return None
