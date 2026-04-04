"""
Ultron Empire — Structured Request Logging Middleware
"""

import json
import logging
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("ultron.access")

# Paths to suppress from routine logging (noisy health-checks etc.)
_QUIET_PATHS = {"/health", "/health/"}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every HTTP request in structured JSON format."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.monotonic()

        response = await call_next(request)

        elapsed_ms = round((time.monotonic() - start) * 1000, 2)
        path = request.url.path

        # Skip noisy health-check logs
        if path in _QUIET_PATHS:
            return response

        log_data = {
            "method": request.method,
            "path": path,
            "status": response.status_code,
            "duration_ms": elapsed_ms,
            "client_ip": (
                request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
                or (request.client.host if request.client else "unknown")
            ),
        }

        log_line = json.dumps(log_data)

        if response.status_code >= 500:
            logger.error(log_line)
        elif response.status_code >= 400:
            logger.warning(log_line)
        else:
            logger.info(log_line)

        return response
