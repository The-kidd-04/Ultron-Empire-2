"""
Ultron Empire — FII/DII Flow Tracker
Fetches daily institutional flow data from NSE.
"""

import logging
from datetime import date
import httpx

from backend.db.database import SessionLocal
from backend.db.models import MarketData

logger = logging.getLogger(__name__)

NSE_FII_URL = "https://www.nseindia.com/api/fiidiiTradeReact"


async def fetch_fii_dii_data() -> dict:
    """Fetch FII/DII data from NSE API."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/",
        }
        async with httpx.AsyncClient() as client:
            # First hit the main page for cookies
            await client.get("https://www.nseindia.com/", headers=headers, timeout=10)
            response = await client.get(NSE_FII_URL, headers=headers, timeout=15)
            data = response.json()

        fii_buy = fii_sell = dii_buy = dii_sell = 0.0
        for entry in data:
            category = entry.get("category", "")
            if "FII" in category or "FPI" in category:
                fii_buy += float(entry.get("buyValue", 0))
                fii_sell += float(entry.get("sellValue", 0))
            elif "DII" in category:
                dii_buy += float(entry.get("buyValue", 0))
                dii_sell += float(entry.get("sellValue", 0))

        fii_net = fii_buy - fii_sell
        dii_net = dii_buy - dii_sell

        return {
            "fii_buy": round(fii_buy, 2),
            "fii_sell": round(fii_sell, 2),
            "fii_net": round(fii_net, 2),
            "fii_direction": "Bought" if fii_net > 0 else "Sold",
            "dii_buy": round(dii_buy, 2),
            "dii_sell": round(dii_sell, 2),
            "dii_net": round(dii_net, 2),
            "dii_direction": "Bought" if dii_net > 0 else "Sold",
        }
    except Exception as e:
        logger.error(f"FII/DII data fetch failed: {e}")
        return {"error": str(e)}


def store_fii_dii(flow_data: dict, for_date: date = None):
    """Store FII/DII data in market_data table."""
    if "error" in flow_data:
        return
    session = SessionLocal()
    try:
        target_date = for_date or date.today()
        record = session.query(MarketData).filter(MarketData.date == target_date).first()
        if record:
            record.fii_buy = flow_data.get("fii_buy")
            record.fii_sell = flow_data.get("fii_sell")
            record.fii_net = flow_data.get("fii_net")
            record.dii_buy = flow_data.get("dii_buy")
            record.dii_sell = flow_data.get("dii_sell")
            record.dii_net = flow_data.get("dii_net")
        else:
            record = MarketData(
                date=target_date,
                fii_buy=flow_data.get("fii_buy"),
                fii_sell=flow_data.get("fii_sell"),
                fii_net=flow_data.get("fii_net"),
                dii_buy=flow_data.get("dii_buy"),
                dii_sell=flow_data.get("dii_sell"),
                dii_net=flow_data.get("dii_net"),
            )
            session.add(record)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"FII/DII store failed: {e}")
    finally:
        session.close()
