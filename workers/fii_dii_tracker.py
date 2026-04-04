"""
Ultron Empire — FII/DII Flow Tracker
Fetches daily FII/DII flow data at 6 PM IST.
"""

import logging
from workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="workers.fii_dii_tracker.update_flows")
def update_flows():
    """Fetch FII/DII flow data from NSE."""
    logger.info("Fetching FII/DII flow data...")
    # In production: scrape NSE for FII/DII data
    # Store in market_data table
    logger.info("FII/DII tracker: pending NSE scraper integration.")
