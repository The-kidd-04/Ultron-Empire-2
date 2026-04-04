"""
Ultron Empire — PMS Data Refresh Worker
Refreshes PMS performance data from all sources (5th of every month).
"""

import asyncio
import logging
from workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="workers.pms_data_refresh.refresh_all")
def refresh_all():
    """Refresh all PMS/AIF performance data."""
    asyncio.run(_refresh_async())


async def _refresh_async():
    from backend.data.pms_scraper import update_pms_data_from_scrape
    from backend.alerts.telegram_bot import send_alert_to_telegram

    logger.info("Monthly PMS data refresh starting...")

    try:
        await update_pms_data_from_scrape()
        await send_alert_to_telegram("📊 Monthly PMS data refresh complete.", "info")
    except Exception as e:
        logger.error(f"PMS data refresh failed: {e}")
        await send_alert_to_telegram(f"⚠️ PMS data refresh failed: {str(e)[:200]}", "important")

    logger.info("PMS data refresh done.")
