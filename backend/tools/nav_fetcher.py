"""
Ultron Empire — NAV Fetcher Tool
Fetches current and historical NAV data for PMS/MF.
"""

from langchain_core.tools import tool
from backend.db.database import SessionLocal
from backend.db.models import FundData, NAVHistory
import logging

logger = logging.getLogger(__name__)


@tool
def nav_fetcher_tool(fund_name: str, period: str = "1m") -> str:
    """Get current and historical NAV data for a fund.

    Args:
        fund_name: Name of the fund (partial match)
        period: Historical period — "1d", "1w", "1m", "3m", "6m", "1y"

    Returns:
        Current NAV and recent NAV history.
    """
    session = SessionLocal()
    try:
        fund = session.query(FundData).filter(
            FundData.fund_name.ilike(f"%{fund_name}%")
        ).first()

        if not fund:
            return f"Fund '{fund_name}' not found in database."

        # Get NAV history
        nav_records = (
            session.query(NAVHistory)
            .filter(NAVHistory.fund_id == fund.id)
            .order_by(NAVHistory.date.desc())
            .limit(30)
            .all()
        )

        result = (
            f"📊 {fund.fund_name}\n"
            f"Fund House: {fund.fund_house}\n"
            f"Category: {fund.category} | Strategy: {fund.strategy}\n\n"
        )

        if nav_records:
            latest = nav_records[0]
            result += f"Latest NAV: ₹{latest.nav:.2f} (as of {latest.date})\n"
            if latest.daily_change_pct is not None:
                result += f"Daily Change: {latest.daily_change_pct:+.2f}%\n"

            result += "\nRecent NAV History:\n"
            for nav in nav_records[:10]:
                chg = f" ({nav.daily_change_pct:+.2f}%)" if nav.daily_change_pct else ""
                result += f"  {nav.date}: ₹{nav.nav:.2f}{chg}\n"
        else:
            result += (
                "No NAV history available yet.\n\n"
                f"Performance (from database):\n"
                f"  1Y: {fund.returns_1y:+.1f}% | 3Y: {fund.returns_3y:+.1f}% | 5Y: {fund.returns_5y:+.1f}%\n"
                f"  Max Drawdown: {fund.max_drawdown}% | Sharpe: {fund.sharpe_ratio}"
            )

        return result
    finally:
        session.close()
