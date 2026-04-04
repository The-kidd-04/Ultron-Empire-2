"""
Ultron Empire — FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.api.router import api_router
from backend.db.database import init_db
from backend.middleware.auth import (
    create_access_token,
    get_current_user,
    _get_valid_api_keys,
    verify_jwt_token,
)
from backend.middleware.rate_limit import RateLimitMiddleware
from backend.middleware.logging_middleware import RequestLoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info("🟢 Ultron Empire starting up...")
    init_db()
    logger.info("Database initialized")

    # Initialize Sentry if configured
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)
            logger.info("Sentry initialized")
        except Exception as e:
            logger.warning(f"Sentry init failed: {e}")

    logger.info(
        "Security middleware active  |  env=%s  |  rate_limit=%d req/min",
        settings.APP_ENV,
        settings.RATE_LIMIT_PER_MINUTE,
    )

    yield

    logger.info("🔴 Ultron Empire shutting down...")


app = FastAPI(
    title="Ultron Empire API",
    description="AI-Powered Wealth Management Operating System — PMS Sahi Hai",
    version="2.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware (order matters — last added runs first)
# ---------------------------------------------------------------------------

# CORS (outermost — runs first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ultron.pmssahihai.com",
        "https://www.pmssahihai.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)

# Request logging (innermost — runs last, closest to route handlers)
app.add_middleware(RequestLoggingMiddleware)

# Mount API routes
app.include_router(api_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Auth token endpoint
# ---------------------------------------------------------------------------

class TokenRequest(BaseModel):
    api_key: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@app.post("/api/v1/auth/token", response_model=TokenResponse, tags=["auth"])
async def create_token(body: TokenRequest):
    """
    Exchange a valid API key for a JWT access token.
    """
    valid_keys = _get_valid_api_keys()

    # In dev mode with no keys configured, accept any non-empty key
    if settings.APP_ENV.lower() == "development" and not valid_keys:
        pass  # allow through
    elif body.api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    token = create_access_token(data={"sub": "api-user", "role": "service"})
    return TokenResponse(
        access_token=token,
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
    )


# ---------------------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "name": "Ultron Empire",
        "version": "2.0.0",
        "status": "online",
        "company": "PMS Sahi Hai",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
