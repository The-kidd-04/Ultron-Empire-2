"""
Ultron Empire — News Scanner Worker
Scans news sources every 15 minutes for market-moving events.
"""

import asyncio
import logging
from workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="workers.news_scanner.scan_news")
def scan_news():
    """Scan for market-moving news."""
    asyncio.run(_scan_news_async())


async def _scan_news_async():
    from backend.tools.news_search import news_search_tool
    from backend.graphs.alert_graph import alert_pipeline

    try:
        # Search for breaking financial news
        results = news_search_tool.invoke({
            "query": "India market PMS AIF SEBI breaking",
            "max_results": 3,
        })

        if results and "No recent news" not in results:
            logger.info(f"News scan found results: {results[:100]}...")
            # In production: parse results, classify significance,
            # and feed into alert pipeline if important enough
    except Exception as e:
        logger.error(f"News scanner failed: {e}")
