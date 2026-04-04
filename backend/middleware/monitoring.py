"""
Prometheus-compatible monitoring middleware for FastAPI.

Tracks request counts, response times, active connections, and error rates.
Exposes metrics at /metrics in Prometheus text format.
"""

import time
from collections import defaultdict
from contextlib import asynccontextmanager
from threading import Lock
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from fastapi.routing import APIRoute


class MetricsStore:
    """Thread-safe in-process metrics store."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.request_count: dict[str, int] = defaultdict(int)
        self.error_count: dict[str, int] = defaultdict(int)
        self.active_connections: int = 0
        self.response_time_sum: dict[str, float] = defaultdict(float)
        self.response_time_count: dict[str, int] = defaultdict(int)
        # Histogram buckets in seconds
        self.histogram_buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        self.response_time_bucket: dict[str, int] = defaultdict(int)

    def record_request(self, method: str, path: str, status: int, duration: float) -> None:
        with self._lock:
            label = f'{method}|{path}|{status}'
            self.request_count[label] += 1
            self.response_time_sum[f'{method}|{path}'] += duration
            self.response_time_count[f'{method}|{path}'] += 1

            # Histogram buckets
            for bucket in self.histogram_buckets:
                if duration <= bucket:
                    self.response_time_bucket[f'{method}|{path}|{bucket}'] += 1

            if status >= 400:
                self.error_count[f'{method}|{path}|{status}'] += 1

    def inc_connections(self) -> None:
        with self._lock:
            self.active_connections += 1

    def dec_connections(self) -> None:
        with self._lock:
            self.active_connections -= 1

    def format_prometheus(self) -> str:
        """Render all metrics in Prometheus text exposition format."""
        lines: list[str] = []

        with self._lock:
            # Request count
            lines.append("# HELP http_requests_total Total number of HTTP requests.")
            lines.append("# TYPE http_requests_total counter")
            for label, count in sorted(self.request_count.items()):
                method, path, status = label.split("|")
                lines.append(
                    f'http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}'
                )

            # Error count
            lines.append("")
            lines.append("# HELP http_errors_total Total number of HTTP error responses (4xx/5xx).")
            lines.append("# TYPE http_errors_total counter")
            for label, count in sorted(self.error_count.items()):
                method, path, status = label.split("|")
                lines.append(
                    f'http_errors_total{{method="{method}",path="{path}",status="{status}"}} {count}'
                )

            # Active connections
            lines.append("")
            lines.append("# HELP http_active_connections Current number of active connections.")
            lines.append("# TYPE http_active_connections gauge")
            lines.append(f"http_active_connections {self.active_connections}")

            # Response time histogram
            lines.append("")
            lines.append(
                "# HELP http_request_duration_seconds HTTP request duration in seconds."
            )
            lines.append("# TYPE http_request_duration_seconds histogram")
            for label, total in sorted(self.response_time_sum.items()):
                method, path = label.split("|")
                count = self.response_time_count[label]
                for bucket in self.histogram_buckets:
                    bucket_key = f"{method}|{path}|{bucket}"
                    bucket_count = self.response_time_bucket.get(bucket_key, 0)
                    lines.append(
                        f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="{bucket}"}} {bucket_count}'
                    )
                lines.append(
                    f'http_request_duration_seconds_bucket{{method="{method}",path="{path}",le="+Inf"}} {count}'
                )
                lines.append(
                    f'http_request_duration_seconds_sum{{method="{method}",path="{path}"}} {total:.6f}'
                )
                lines.append(
                    f'http_request_duration_seconds_count{{method="{method}",path="{path}"}} {count}'
                )

        lines.append("")
        return "\n".join(lines)


# Module-level singleton so the middleware and endpoint share state.
metrics = MetricsStore()


def _normalize_path(request: Request) -> str:
    """Collapse path parameters to reduce cardinality (e.g. /users/123 -> /users/{id})."""
    for route in request.app.routes:
        if isinstance(route, APIRoute) and route.path_regex.match(request.url.path):
            return route.path
    return request.url.path


async def monitoring_middleware(request: Request, call_next: Callable) -> Response:
    """FastAPI middleware that records per-request metrics."""
    if request.url.path == "/metrics":
        return await call_next(request)

    metrics.inc_connections()
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration = time.perf_counter() - start
        path = _normalize_path(request)
        metrics.record_request(request.method, path, 500, duration)
        metrics.dec_connections()
        raise

    duration = time.perf_counter() - start
    path = _normalize_path(request)
    metrics.record_request(request.method, path, response.status_code, duration)
    metrics.dec_connections()

    return response


def metrics_endpoint(_request: Request) -> PlainTextResponse:
    """Handler for GET /metrics."""
    return PlainTextResponse(metrics.format_prometheus(), media_type="text/plain; version=0.0.4")


def setup_monitoring(app: FastAPI) -> None:
    """
    Wire monitoring into a FastAPI app.

    Usage in main.py:
        from backend.middleware.monitoring import setup_monitoring
        setup_monitoring(app)
    """
    app.middleware("http")(monitoring_middleware)
    app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], include_in_schema=False)
