"""
Redis cache wrapper for real-time price data, sessions, and flag calculations.
"""
import json
from typing import Optional, Any

import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()


class RedisCache:
    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def connect(self):
        self._redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def disconnect(self):
        if self._redis:
            await self._redis.close()

    async def get(self, key: str) -> Optional[str]:
        if not self._redis:
            await self.connect()
        return await self._redis.get(key)

    async def set(self, key: str, value: Any, ex: int = 60):
        if not self._redis:
            await self.connect()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self._redis.set(key, str(value), ex=ex)

    async def delete(self, key: str):
        if not self._redis:
            await self.connect()
        await self._redis.delete(key)

    async def get_json(self, key: str) -> Optional[Any]:
        raw = await self.get(key)
        if raw:
            return json.loads(raw)
        return None

    async def set_json(self, key: str, value: Any, ex: int = 60):
        await self.set(key, json.dumps(value), ex=ex)

    # Price-specific helpers
    async def get_price(self, ticker: str) -> Optional[float]:
        val = await self.get(f"price:{ticker}")
        return float(val) if val else None

    async def set_price(self, ticker: str, price: float, ex: int = 120):
        await self.set(f"price:{ticker}", str(price), ex=ex)

    async def get_flag_score(self, ticker: str) -> Optional[int]:
        val = await self.get(f"flag_score:{ticker}")
        return int(val) if val else None

    async def set_flag_score(self, ticker: str, score: int, ex: int = 300):
        await self.set(f"flag_score:{ticker}", str(score), ex=ex)
