"""
Ultron Empire — FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.api.router import api_router
from backend.db.database import init_db

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

    yield

    logger.info("🔴 Ultron Empire shutting down...")


app = FastAPI(
    title="Ultron Empire API",
    description="AI-Powered Wealth Management Operating System — PMS Sahi Hai",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
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

# Mount API routes
app.include_router(api_router, prefix="/api/v1")


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
