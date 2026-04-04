"""
Structured JSON logging with correlation ID support.

In production (ENVIRONMENT != "development"), logs are emitted as single-line
JSON objects suitable for ingestion by ELK, Datadog, etc.
In development, logs use a coloured human-readable format.

Usage:
    from backend.utils.structured_logging import setup_logging, get_logger

    setup_logging()                     # call once at startup
    logger = get_logger(__name__)       # per-module logger
    logger.info("hello", extra={"user_id": 42})
"""

import json
import logging
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

# Context variable that carries the correlation / request ID across async calls.
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """Return the current correlation ID, or empty string if none is set."""
    return correlation_id_var.get()


def set_correlation_id(cid: str | None = None) -> str:
    """Set (or generate) a correlation ID for the current context. Returns the ID."""
    cid = cid or uuid.uuid4().hex
    correlation_id_var.set(cid)
    return cid


# ---------------------------------------------------------------------------
# JSON Formatter
# ---------------------------------------------------------------------------

class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Correlation / request ID
        cid = get_correlation_id()
        if cid:
            log_entry["request_id"] = cid

        # Source location
        log_entry["module"] = record.module
        log_entry["function"] = record.funcName
        log_entry["line"] = record.lineno

        # Exception info
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Merge any extra fields the caller passed via `extra={...}`
        standard_attrs = logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys()
        for key, value in record.__dict__.items():
            if key not in standard_attrs and key not in log_entry:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


# ---------------------------------------------------------------------------
# Human-readable formatter (development)
# ---------------------------------------------------------------------------

class DevFormatter(logging.Formatter):
    """Coloured, human-readable formatter for local development."""

    COLOURS = {
        "DEBUG": "\033[36m",     # cyan
        "INFO": "\033[32m",      # green
        "WARNING": "\033[33m",   # yellow
        "ERROR": "\033[31m",     # red
        "CRITICAL": "\033[1;31m",  # bold red
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        colour = self.COLOURS.get(record.levelname, "")
        cid = get_correlation_id()
        cid_part = f" [{cid[:8]}]" if cid else ""
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        base = (
            f"{colour}{timestamp} {record.levelname:<8}{self.RESET}"
            f"{cid_part} {record.name}: {record.getMessage()}"
        )
        if record.exc_info and record.exc_info[0] is not None:
            base += "\n" + self.formatException(record.exc_info)
        return base


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def setup_logging(
    level: str | None = None,
    environment: str | None = None,
) -> None:
    """
    Configure the root logger.

    Parameters
    ----------
    level : str, optional
        Log level name (DEBUG, INFO, ...). Defaults to LOG_LEVEL env var or INFO.
    environment : str, optional
        "development" for human-readable output, anything else for JSON.
        Defaults to ENVIRONMENT env var or "production".
    """
    level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    environment = environment or os.getenv("ENVIRONMENT", "production")

    root = logging.getLogger()
    root.setLevel(level)

    # Remove existing handlers to avoid duplicate output on repeat calls
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if environment.lower() == "development":
        handler.setFormatter(DevFormatter())
    else:
        handler.setFormatter(JSONFormatter())

    root.addHandler(handler)

    # Quiet noisy third-party loggers
    for noisy in ("uvicorn.access", "httpx", "httpcore", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger (convenience wrapper)."""
    return logging.getLogger(name)
