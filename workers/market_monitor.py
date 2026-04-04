"""
Ultron Empire — Market Monitor Worker
Checks market conditions every 5 minutes during trading hours.
"""

import asyncio
import logging
from workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="workers.market_monitor.check_market")
def check_market():
    """Monitor market for significant moves."""
    asyncio.run(_check_market_async())


async def _check_market_async():
    from backend.tools.market_data import market_data_tool
    from backend.alerts.telegram_bot import send_alert_to_telegram
    from backend.alerts.engine import store_alert

    try:
        data = market_data_tool.invoke({"indicator": "nifty"})

        # Parse for significant moves (simplified — enhance with real parsing)
        if "N/A" not in data:
            # Check for large moves (>1.5% intraday)
            # In production, parse the actual numbers
            logger.info(f"Market check complete. Data: {data[:100]}...")
    except Exception as e:
        logger.error(f"Market monitor failed: {e}")
