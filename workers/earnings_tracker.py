"""
Ultron Empire — Earnings Tracker Worker
Monitors corporate earnings during results season.
"""

import asyncio
import logging
from workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="workers.earnings_tracker.check_earnings")
def check_earnings():
    """Check for upcoming and recent earnings results."""
    asyncio.run(_check_earnings_async())


async def _check_earnings_async():
    from backend.data.earnings_tracker import get_upcoming_earnings, check_earnings_impact
    from backend.alerts.telegram_bot import send_alert_to_telegram

    try:
        upcoming = get_upcoming_earnings(days_ahead=3)
        tracked = upcoming.get("tracked_stocks", [])

        if tracked:
            logger.info(f"Earnings tracker: monitoring {len(tracked)} stocks in PMS portfolios")
    except Exception as e:
        logger.error(f"Earnings tracker failed: {e}")
