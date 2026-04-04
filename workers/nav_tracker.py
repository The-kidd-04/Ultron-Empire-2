"""
Ultron Empire — NAV Tracker Worker
Fetches latest NAVs daily at 9 PM IST.
"""

import logging
from workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="workers.nav_tracker.update_navs")
def update_navs():
    """Fetch and store latest NAV data."""
    from backend.db.database import SessionLocal
    from backend.db.models import FundData

    logger.info("Updating NAV data...")
    session = SessionLocal()

    try:
        # In production: fetch from AMFI API for MFs, scrape PMS websites
        # For now, log that the task ran
        fund_count = session.query(FundData).count()
        logger.info(f"NAV tracker: {fund_count} funds in database. Update pending API integration.")
    except Exception as e:
        logger.error(f"NAV update failed: {e}")
    finally:
        session.close()
