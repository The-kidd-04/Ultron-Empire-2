"""
Ultron Empire — Market API
GET /market — Market data and indicators.
"""

import logging

from fastapi import APIRouter, Query
from typing import List, Optional

from backend.db.database import SessionLocal
from backend.db.models import MarketData

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def get_market_data(indicator: Optional[str] = "overview"):
    """Get current market data. Returns structured JSON for dashboard consumption."""
    try:
        from backend.tools.market_data import market_data_tool
        result = market_data_tool.invoke({"indicator": indicator})
    except Exception as e:
        logger.warning(f"Market data tool failed: {e}")
        result = None

    # Try to get structured data from database
    session = SessionLocal()
    try:
        latest = session.query(MarketData).order_by(MarketData.date.desc()).first()
        if latest:
            return {
                "nifty": latest.nifty_close,
                "nifty_change_pct": latest.nifty_change_pct,
                "nifty_pe": latest.nifty_pe,
                "sensex": latest.sensex_close if hasattr(latest, 'sensex_close') else None,
                "vix": latest.india_vix,
                "fii_net": latest.fii_net,
                "dii_net": latest.dii_net,
                "data": result,
            }
    except Exception as e:
        logger.warning(f"Database market data query failed: {e}")
    finally:
        session.close()

    # Fallback sample data so dashboards always have something to show
    return {
        "nifty": 22480,
        "nifty_change_pct": 0.62,
        "sensex": 73950,
        "vix": 13.2,
        "fii_net": 1280,
        "dii_net": 890,
        "data": result or "Market data (sample — yfinance not installed)",
    }


@router.get("/history")
async def get_market_history(days: int = Query(default=30, le=365)):
    """Get historical market data."""
    session = SessionLocal()
    try:
        records = (
            session.query(MarketData)
            .order_by(MarketData.date.desc())
            .limit(days)
            .all()
        )
        return [
            {
                "date": str(r.date),
                "nifty_close": r.nifty_close,
                "nifty_change_pct": r.nifty_change_pct,
                "nifty_pe": r.nifty_pe,
                "india_vix": r.india_vix,
                "fii_net": r.fii_net,
                "dii_net": r.dii_net,
            }
            for r in records
        ]
    finally:
        session.close()


@router.get("/earnings")
async def get_earnings_calendar(stocks: Optional[str] = Query(default=None, description="Comma-separated stock names, or omit for all tracked stocks")):
    """Return upcoming earnings dates for tracked Indian stocks via yfinance."""
    from backend.data.earnings_tracker import get_upcoming_earnings

    stock_list = None
    if stocks:
        stock_list = [s.strip() for s in stocks.split(",") if s.strip()]

    return {
        "earnings": get_upcoming_earnings(stocks=stock_list),
    }
