"""
Ultron Empire — Celery Application
Task queue configuration with Redis broker.
"""

from celery import Celery
from backend.config import settings

app = Celery(
    "ultron",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "workers.market_monitor",
        "workers.news_scanner",
        "workers.daily_brief",
        "workers.nav_tracker",
        "workers.fii_dii_tracker",
        "workers.sebi_checker",
        "workers.client_reminders",
        "workers.weekly_recap",
        "workers.prediction_updater",
    ],
)

app.config_from_object("workers.celery_config")
