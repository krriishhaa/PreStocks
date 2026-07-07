"""
Request logging middleware.
Captures all API requests per §8 Backend Logging:
- method, path, status_code, response_time_ms
- user_id (if authenticated)
"""
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every API request with timing and metadata."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        # Extract user info if available
        user_id = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from app.core.security import decode_token
                payload = decode_token(auth_header.split(" ")[1])
                user_id = payload.get("sub")
            except Exception:
                pass

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log the request
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "response_time_ms": round(duration_ms, 2),
            "user_id": user_id,
            "query_params": str(request.query_params) if request.query_params else None,
        }

        # Choose log level based on status code
        if response.status_code >= 500:
            logger.error(f"API {log_data['method']} {log_data['path']} → {log_data['status_code']} ({log_data['response_time_ms']}ms)", extra=log_data)
        elif response.status_code >= 400:
            logger.warning(f"API {log_data['method']} {log_data['path']} → {log_data['status_code']} ({log_data['response_time_ms']}ms)", extra=log_data)
        else:
            logger.info(f"API {log_data['method']} {log_data['path']} → {log_data['status_code']} ({log_data['response_time_ms']}ms)", extra=log_data)

        # Add response time header
        response.headers["X-Response-Time"] = f"{duration_ms:.0f}ms"

        return response
