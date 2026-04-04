"""
Ultron Empire — Earnings Tracker
Tracks corporate earnings calendar and results for PMS-held stocks.
"""

import logging
from datetime import date, timedelta
from backend.db.database import SessionLocal
from backend.db.models import FundData

logger = logging.getLogger(__name__)


def get_upcoming_earnings(days_ahead: int = 7) -> list:
    """Get upcoming earnings for stocks held in tracked PMS portfolios."""
    session = SessionLocal()
    try:
        funds = session.query(FundData).all()
        all_stocks = set()
        for fund in funds:
            for stock in (fund.top_holdings or []):
                all_stocks.add(stock)

        # In production: cross-reference with earnings calendar from BSE/NSE
        # For now, return the stock universe
        return {
            "tracked_stocks": sorted(all_stocks),
            "total_stocks": len(all_stocks),
            "note": "Earnings calendar requires BSE/NSE API integration",
        }
    finally:
        session.close()


def check_earnings_impact(stock: str, result_type: str, surprise_pct: float) -> dict:
    """Analyze earnings impact on PMS portfolios.

    Args:
        stock: Stock name (e.g., "HDFC Bank")
        result_type: "beat", "miss", or "inline"
        surprise_pct: Earnings surprise percentage
    """
    session = SessionLocal()
    try:
        affected_funds = []
        funds = session.query(FundData).all()
        for fund in funds:
            if stock in (fund.top_holdings or []):
                affected_funds.append({
                    "fund": fund.fund_name,
                    "house": fund.fund_house,
                    "category": fund.category,
                })

        severity = "critical" if abs(surprise_pct) > 10 else "important" if abs(surprise_pct) > 5 else "info"

        return {
            "stock": stock,
            "result_type": result_type,
            "surprise_pct": surprise_pct,
            "affected_funds": affected_funds,
            "severity": severity,
        }
    finally:
        session.close()
