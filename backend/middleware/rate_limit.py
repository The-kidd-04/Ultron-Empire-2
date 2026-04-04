"""
Ultron Empire — Token-Bucket Rate Limiter (in-memory)
"""

import time
from typing import Dict, Optional, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from backend.config import settings


class _TokenBucket:
    """Simple token-bucket for a single client."""

    __slots__ = ("capacity", "tokens", "refill_rate", "last_refill")

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_rate = refill_rate          # tokens per second
        self.last_refill = time.monotonic()

    def consume(self) -> Tuple[bool, float]:
        """Try to consume one token.

        Returns (allowed, retry_after_seconds).
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True, 0.0
        else:
            retry_after = (1 - self.tokens) / self.refill_rate
            return False, retry_after


# Per-route overrides: path -> requests per minute
_route_limits: Dict[str, int] = {}


def set_route_limit(path: str, requests_per_minute: int) -> None:
    """Register a custom rate limit for a specific route prefix."""
    _route_limits[path] = requests_per_minute


def _get_limit_for_path(path: str) -> int:
    """Return the rate limit (req/min) for a path, checking overrides first."""
    for prefix, limit in _route_limits.items():
        if path.startswith(prefix):
            return limit
    return settings.RATE_LIMIT_PER_MINUTE


def _client_ip(request: Request) -> str:
    """Extract the client IP, respecting X-Forwarded-For when present."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that applies per-IP token-bucket rate limiting."""

    def __init__(self, app, default_rpm: Optional[int] = None):
        super().__init__(app)
        self.default_rpm = default_rpm or settings.RATE_LIMIT_PER_MINUTE
        # bucket key -> _TokenBucket
        self._buckets: Dict[str, _TokenBucket] = {}

    def _get_bucket(self, key: str, rpm: int) -> _TokenBucket:
        bucket = self._buckets.get(key)
        if bucket is None or bucket.capacity != rpm:
            bucket = _TokenBucket(capacity=rpm, refill_rate=rpm / 60.0)
            self._buckets[key] = bucket
        return bucket

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        ip = _client_ip(request)
        path = request.url.path
        rpm = _get_limit_for_path(path)

        bucket_key = f"{ip}:{rpm}"
        bucket = self._get_bucket(bucket_key, rpm)

        allowed, retry_after = bucket.consume()
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please slow down.",
                },
                headers={"Retry-After": str(int(retry_after) + 1)},
            )

        response = await call_next(request)
        # Informational headers
        response.headers["X-RateLimit-Limit"] = str(rpm)
        response.headers["X-RateLimit-Remaining"] = str(max(0, int(bucket.tokens)))
        return response
