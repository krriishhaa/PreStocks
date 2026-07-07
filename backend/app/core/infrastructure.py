"""
Infrastructure: Rate Limiting, Caching, Monitoring, Logging.
Production-grade middleware stack for PreStocks API.
"""

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from datetime import datetime, timedelta
from collections import defaultdict
import time
import logging
import json
import asyncio
from typing import Optional, Dict, Tuple

logger = logging.getLogger("prestocks.infra")


# ═══════════════════════════════════════════════════
# RATE LIMITER (Token Bucket Algorithm)
# ═══════════════════════════════════════════════════

class RateLimiter:
    """
    In-memory token bucket rate limiter.
    For production, replace with Redis-backed implementation.
    """
    def __init__(self):
        self.buckets: Dict[str, Tuple[float, float]] = {}
        self.rules = {
            "default": {"capacity": 60, "refill_rate": 1.0},
            "auth": {"capacity": 10, "refill_rate": 0.2},
            "ai": {"capacity": 20, "refill_rate": 0.5},
            "search": {"capacity": 30, "refill_rate": 1.0},
        }

    def get_rule(self, path: str) -> dict:
        if "/auth/" in path:
            return self.rules["auth"]
        elif "/ai/" in path:
            return self.rules["ai"]
        elif "/search" in path:
            return self.rules["search"]
        return self.rules["default"]

    def is_allowed(self, key: str, path: str) -> Tuple[bool, dict]:
        rule = self.get_rule(path)
        now = time.time()

        if key not in self.buckets:
            self.buckets[key] = (rule["capacity"] - 1, now)
            return True, {
                "X-RateLimit-Limit": str(rule["capacity"]),
                "X-RateLimit-Remaining": str(rule["capacity"] - 1),
                "X-RateLimit-Reset": str(int(now + rule["capacity"] / rule["refill_rate"]))
            }

        tokens, last_time = self.buckets[key]
        elapsed = now - last_time
        tokens = min(rule["capacity"], tokens + elapsed * rule["refill_rate"])

        if tokens < 1:
            retry_after = int((1 - tokens) / rule["refill_rate"])
            return False, {
                "X-RateLimit-Limit": str(rule["capacity"]),
                "X-RateLimit-Remaining": "0",
                "Retry-After": str(retry_after)
            }

        tokens -= 1
        self.buckets[key] = (tokens, now)
        return True, {
            "X-RateLimit-Limit": str(rule["capacity"]),
            "X-RateLimit-Remaining": str(int(tokens)),
            "X-RateLimit-Reset": str(int(now + (rule["capacity"] - tokens) / rule["refill_rate"]))
        }


rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/docs", "/redoc", "/openapi.json", "/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        auth_header = request.headers.get("Authorization", "")
        key = auth_header[:20] if auth_header else client_ip

        allowed, headers = rate_limiter.is_allowed(key, request.url.path)

        if not allowed:
            return Response(
                content=json.dumps({"detail": "Rate limit exceeded. Please retry later."}),
                status_code=429,
                media_type="application/json",
                headers=headers
            )

        response = await call_next(request)
        for k, v in headers.items():
            response.headers[k] = v
        return response


# ═══════════════════════════════════════════════════
# RESPONSE CACHING
# ═══════════════════════════════════════════════════

class ResponseCache:
    """
    In-memory LRU cache for GET endpoints.
    For production, replace with Redis.
    """
    def __init__(self, max_size: int = 1000, default_ttl: int = 60):
        self.cache: Dict[str, Tuple[bytes, str, float]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Tuple[bytes, str]]:
        if key in self.cache:
            body, content_type, expires_at = self.cache[key]
            if time.time() < expires_at:
                self.hits += 1
                return body, content_type
            else:
                del self.cache[key]
        self.misses += 1
        return None

    def set(self, key: str, body: bytes, content_type: str, ttl: Optional[int] = None):
        if len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = (body, content_type, time.time() + (ttl or self.default_ttl))

    def invalidate(self, pattern: str):
        keys_to_delete = [k for k in self.cache if pattern in k]
        for k in keys_to_delete:
            del self.cache[k]

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{(self.hits / total * 100):.1f}%" if total > 0 else "0%"
        }


response_cache = ResponseCache()

CACHEABLE_PREFIXES = ["/companies/", "/sectors/", "/tags/", "/news/trending"]
CACHE_TTL_MAP = {
    "/companies/search": 30,
    "/companies/sectors": 300,
    "/companies/tags": 300,
    "/news/trending": 60,
}


class CacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != "GET":
            return await call_next(request)

        path = request.url.path
        if not any(path.startswith(p) for p in CACHEABLE_PREFIXES):
            return await call_next(request)

        cache_key = f"{path}?{request.url.query}"
        cached = response_cache.get(cache_key)
        if cached:
            body, content_type = cached
            return Response(
                content=body,
                media_type=content_type,
                headers={"X-Cache": "HIT"}
            )

        response = await call_next(request)

        if response.status_code == 200:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            ttl = next((v for k, v in CACHE_TTL_MAP.items() if path.startswith(k)), 60)
            response_cache.set(cache_key, body, response.media_type or "application/json", ttl)

            return Response(
                content=body,
                status_code=response.status_code,
                media_type=response.media_type,
                headers={**dict(response.headers), "X-Cache": "MISS"}
            )

        return response


# ═══════════════════════════════════════════════════
# REQUEST MONITORING & METRICS
# ═══════════════════════════════════════════════════

class MetricsCollector:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_latency_ms = 0
        self.endpoint_stats: Dict[str, Dict] = defaultdict(
            lambda: {"count": 0, "errors": 0, "total_ms": 0, "p99_ms": 0}
        )
        self.status_codes: Dict[int, int] = defaultdict(int)
        self.started_at = datetime.utcnow()

    def record(self, path: str, method: str, status_code: int, latency_ms: float):
        self.request_count += 1
        self.total_latency_ms += latency_ms
        self.status_codes[status_code] += 1

        if status_code >= 400:
            self.error_count += 1

        key = f"{method} {path}"
        self.endpoint_stats[key]["count"] += 1
        self.endpoint_stats[key]["total_ms"] += latency_ms
        if status_code >= 400:
            self.endpoint_stats[key]["errors"] += 1

    def get_summary(self) -> dict:
        uptime = (datetime.utcnow() - self.started_at).total_seconds()
        avg_latency = self.total_latency_ms / self.request_count if self.request_count > 0 else 0

        top_endpoints = sorted(
            self.endpoint_stats.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:10]

        return {
            "uptime_seconds": int(uptime),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": f"{(self.error_count / self.request_count * 100):.2f}%" if self.request_count > 0 else "0%",
            "avg_latency_ms": round(avg_latency, 2),
            "requests_per_second": round(self.request_count / uptime, 2) if uptime > 0 else 0,
            "status_codes": dict(self.status_codes),
            "top_endpoints": [
                {"endpoint": k, "requests": v["count"], "avg_ms": round(v["total_ms"] / v["count"], 1)}
                for k, v in top_endpoints
            ],
            "cache_stats": response_cache.stats()
        }


metrics = MetricsCollector()


class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()

        response = await call_next(request)

        latency_ms = (time.time() - start) * 1000
        metrics.record(request.url.path, request.method, response.status_code, latency_ms)

        response.headers["X-Response-Time"] = f"{latency_ms:.0f}ms"
        response.headers["X-Request-Id"] = request.headers.get("X-Request-Id", str(int(time.time() * 1000)))

        if latency_ms > 5000:
            logger.warning(f"Slow request: {request.method} {request.url.path} took {latency_ms:.0f}ms")

        return response


# ═══════════════════════════════════════════════════
# STRUCTURED LOGGING
# ═══════════════════════════════════════════════════

class StructuredLogger:
    def __init__(self, name: str = "prestocks"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '{"time":"%(asctime)s","level":"%(levelname)s","module":"%(module)s","message":"%(message)s"}'
            ))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def info(self, message: str, **kwargs):
        self.logger.info(json.dumps({"msg": message, **kwargs}))

    def error(self, message: str, **kwargs):
        self.logger.error(json.dumps({"msg": message, **kwargs}))

    def warn(self, message: str, **kwargs):
        self.logger.warning(json.dumps({"msg": message, **kwargs}))


app_logger = StructuredLogger()
