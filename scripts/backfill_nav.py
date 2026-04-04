"""Backfill historical NAV data using yfinance."""

import logging
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("NAV backfill: Requires yfinance historical data pull + AMFI API. Run: python -m backend.data.nav_tracker")
