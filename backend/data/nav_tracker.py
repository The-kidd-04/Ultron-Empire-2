"""
Ultron Empire — NAV Tracker Pipeline
Fetches daily NAV data from AMFI for mutual funds and scrapes PMS sources.
"""

import logging
from datetime import date, datetime, timezone
import httpx

from backend.db.database import SessionLocal
from backend.db.models import NAVHistory, FundData

logger = logging.getLogger(__name__)

AMFI_NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt"


async def fetch_amfi_navs() -> dict:
    """Fetch latest NAV data from AMFI for all mutual funds."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(AMFI_NAV_URL, timeout=30)
            response.raise_for_status()

        navs = {}
        for line in response.text.split("\n"):
            parts = line.strip().split(";")
            if len(parts) >= 5:
                try:
                    scheme_code = parts[0].strip()
                    nav_value = float(parts[4].strip())
                    scheme_name = parts[3].strip()
                    nav_date = parts[7].strip() if len(parts) > 7 else str(date.today())
                    navs[scheme_name] = {"nav": nav_value, "date": nav_date, "code": scheme_code}
                except (ValueError, IndexError):
                    continue
        logger.info(f"Fetched {len(navs)} NAVs from AMFI")
        return navs
    except Exception as e:
        logger.error(f"AMFI NAV fetch failed: {e}")
        return {}


def store_nav(fund_id: int, nav_date: date, nav_value: float, daily_change_pct: float = None):
    """Store a NAV record in the database."""
    session = SessionLocal()
    try:
        existing = session.query(NAVHistory).filter(
            NAVHistory.fund_id == fund_id,
            NAVHistory.date == nav_date,
        ).first()
        if not existing:
            record = NAVHistory(
                fund_id=fund_id,
                date=nav_date,
                nav=nav_value,
                daily_change_pct=daily_change_pct,
            )
            session.add(record)
            session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"NAV store failed for fund {fund_id}: {e}")
    finally:
        session.close()


async def update_all_navs():
    """Update NAVs for all funds in the database."""
    amfi_navs = await fetch_amfi_navs()
    session = SessionLocal()
    try:
        funds = session.query(FundData).filter(FundData.category == "MF").all()
        updated = 0
        for fund in funds:
            if fund.fund_name in amfi_navs:
                nav_data = amfi_navs[fund.fund_name]
                store_nav(fund.id, date.today(), nav_data["nav"])
                updated += 1
        logger.info(f"Updated {updated}/{len(funds)} MF NAVs")
    finally:
        session.close()
