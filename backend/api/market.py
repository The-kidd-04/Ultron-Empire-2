"""
Ultron Empire — Market API
GET /market — Market data and indicators.
"""

from fastapi import APIRouter, Query
from typing import Optional

from backend.db.database import SessionLocal
from backend.db.models import MarketData

router = APIRouter()


@router.get("")
async def get_market_data(indicator: Optional[str] = "overview"):
    """Get current market data. Calls the market_data tool."""
    from backend.tools.market_data import market_data_tool
    result = market_data_tool.invoke({"indicator": indicator})
    return {"data": result}


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
