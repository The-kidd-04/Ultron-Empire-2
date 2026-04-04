"""
Ultron Empire — SEBI Circular Checker
Monitors SEBI website for new circulars hourly during business hours.
"""

import asyncio
import logging
from workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="workers.sebi_checker.check_circulars")
def check_circulars():
    """Check SEBI for new circulars."""
    asyncio.run(_check_circulars_async())


async def _check_circulars_async():
    from backend.tools.sebi_checker import sebi_checker_tool

    try:
        results = sebi_checker_tool.invoke({"query": "PMS AIF mutual fund circular"})
        if results and "unavailable" not in results.lower():
            logger.info(f"SEBI check: {results[:100]}...")
    except Exception as e:
        logger.error(f"SEBI checker failed: {e}")
