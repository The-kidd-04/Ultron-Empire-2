"""
Ultron Empire — FII/DII Flow Tracker
Fetches daily institutional flow data from multiple sources with fallback:
  1. NSE India API (primary)
  2. Moneycontrol public endpoint (secondary)
  3. NSDL website scraping (tertiary)
  4. Sample/placeholder data (last resort)
"""

import logging
import re
from datetime import date
from typing import Optional

import httpx

from backend.db.database import SessionLocal
from backend.db.models import MarketData

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Source URLs
# ---------------------------------------------------------------------------
NSE_FII_URL = "https://www.nseindia.com/api/fiidiiTradeReact"
MONEYCONTROL_FII_URL = "https://api.moneycontrol.com/mcapi/v1/fii-dii/overview"
NSDL_FII_URL = "https://www.fpi.nsdl.co.in/web/Reports/Latest.aspx"

# Common browser-like headers
_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------------------
# Helper: build result dict
# ---------------------------------------------------------------------------

def _build_result(
    fii_buy: float,
    fii_sell: float,
    dii_buy: float,
    dii_sell: float,
    source: str,
) -> dict:
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
        "source": source,
    }


# ---------------------------------------------------------------------------
# Source 1: NSE India API
# ---------------------------------------------------------------------------

async def _fetch_from_nse(client: httpx.AsyncClient) -> Optional[dict]:
    """Fetch FII/DII data from the NSE India API."""
    try:
        headers = {**_BROWSER_HEADERS, "Referer": "https://www.nseindia.com/"}
        # Hit the main page first to establish cookies
        await client.get("https://www.nseindia.com/", headers=headers, timeout=10)
        response = await client.get(NSE_FII_URL, headers=headers, timeout=15)
        response.raise_for_status()
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

        if fii_buy == 0 and dii_buy == 0:
            logger.warning("NSE returned zero values — treating as empty")
            return None

        logger.info("FII/DII data fetched from NSE")
        return _build_result(fii_buy, fii_sell, dii_buy, dii_sell, source="NSE")
    except Exception as e:
        logger.warning("NSE FII/DII fetch failed: %s", e)
        return None


# ---------------------------------------------------------------------------
# Source 2: Moneycontrol public API
# ---------------------------------------------------------------------------

async def _fetch_from_moneycontrol(client: httpx.AsyncClient) -> Optional[dict]:
    """Fetch FII/DII data from Moneycontrol's public API."""
    try:
        headers = {
            **_BROWSER_HEADERS,
            "Referer": "https://www.moneycontrol.com/",
        }
        response = await client.get(MONEYCONTROL_FII_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Moneycontrol wraps data inside a 'data' key
        payload = data.get("data", data)

        fii_buy = float(payload.get("fii_buy", 0) or 0)
        fii_sell = float(payload.get("fii_sell", 0) or 0)
        dii_buy = float(payload.get("dii_buy", 0) or 0)
        dii_sell = float(payload.get("dii_sell", 0) or 0)

        # Try alternate key names used by moneycontrol
        if fii_buy == 0 and "fiiBuyValue" in payload:
            fii_buy = float(payload.get("fiiBuyValue", 0))
            fii_sell = float(payload.get("fiiSellValue", 0))
            dii_buy = float(payload.get("diiBuyValue", 0))
            dii_sell = float(payload.get("diiSellValue", 0))

        if fii_buy == 0 and dii_buy == 0:
            logger.warning("Moneycontrol returned zero values")
            return None

        logger.info("FII/DII data fetched from Moneycontrol")
        return _build_result(fii_buy, fii_sell, dii_buy, dii_sell, source="Moneycontrol")
    except Exception as e:
        logger.warning("Moneycontrol FII/DII fetch failed: %s", e)
        return None


# ---------------------------------------------------------------------------
# Source 3: NSDL website scraping
# ---------------------------------------------------------------------------

def _parse_crore_value(text: str) -> float:
    """Extract a numeric crore value from text like '12,345.67' or '(1,234.56)'."""
    text = text.strip().replace(",", "")
    negative = "(" in text or "-" in text
    nums = re.findall(r"[\d.]+", text)
    if not nums:
        return 0.0
    value = float(nums[0])
    return -value if negative else value


async def _fetch_from_nsdl(client: httpx.AsyncClient) -> Optional[dict]:
    """Scrape FII/DII data from the NSDL FPI monitor page."""
    try:
        headers = {**_BROWSER_HEADERS, "Referer": "https://www.fpi.nsdl.co.in/"}
        response = await client.get(NSDL_FII_URL, headers=headers, timeout=20)
        response.raise_for_status()
        html = response.text

        # Look for FII/FPI buy and sell values in the HTML table
        # NSDL uses a table with columns: Date | Buy | Sell | Net
        buy_pattern = re.findall(
            r"Gross\s+Purchase.*?<td[^>]*>([\d,.\-()]+)</td>", html, re.DOTALL | re.IGNORECASE
        )
        sell_pattern = re.findall(
            r"Gross\s+Sale.*?<td[^>]*>([\d,.\-()]+)</td>", html, re.DOTALL | re.IGNORECASE
        )

        if not buy_pattern or not sell_pattern:
            logger.warning("Could not parse NSDL FPI page — pattern mismatch")
            return None

        fii_buy = _parse_crore_value(buy_pattern[0])
        fii_sell = _parse_crore_value(sell_pattern[0])

        # NSDL only reports FPI data; DII is not available from this source
        logger.info("FII (FPI) data fetched from NSDL — DII not available from this source")
        return _build_result(fii_buy, fii_sell, dii_buy=0, dii_sell=0, source="NSDL (FPI only)")
    except Exception as e:
        logger.warning("NSDL FPI scrape failed: %s", e)
        return None


# ---------------------------------------------------------------------------
# Source 4: Fallback sample data
# ---------------------------------------------------------------------------

def _get_sample_data() -> dict:
    """Return sample FII/DII data when all live sources are unavailable."""
    logger.warning(
        "All live FII/DII sources failed — returning sample data. "
        "Values are illustrative only and should not be used for decisions."
    )
    return {
        **_build_result(
            fii_buy=8500.0,
            fii_sell=9200.0,
            dii_buy=7800.0,
            dii_sell=6500.0,
            source="sample",
        ),
        "is_sample": True,
    }


# ---------------------------------------------------------------------------
# Main fetch function (tries all sources in order)
# ---------------------------------------------------------------------------

async def fetch_fii_dii_data() -> dict:
    """Fetch FII/DII data, trying multiple sources with graceful fallback.

    Tries in order: NSE -> Moneycontrol -> NSDL -> Sample data.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Source 1: NSE
        result = await _fetch_from_nse(client)
        if result:
            return result

        # Source 2: Moneycontrol
        result = await _fetch_from_moneycontrol(client)
        if result:
            return result

        # Source 3: NSDL
        result = await _fetch_from_nsdl(client)
        if result:
            return result

    # Source 4: Sample/fallback
    return _get_sample_data()


# ---------------------------------------------------------------------------
# Database storage
# ---------------------------------------------------------------------------

def store_fii_dii(flow_data: dict, for_date: date = None):
    """Store FII/DII data in the market_data table.

    Skips storage if the data is sample/fallback data (to avoid polluting
    the database with placeholder values).
    """
    if flow_data.get("is_sample"):
        logger.info("Skipping DB storage for sample FII/DII data")
        return
    if "error" in flow_data:
        logger.warning("Skipping DB storage — flow_data contains an error")
        return

    session = SessionLocal()
    try:
        target_date = for_date or date.today()
        record = (
            session.query(MarketData)
            .filter(MarketData.date == target_date)
            .first()
        )
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
        logger.info(
            "FII/DII data stored for %s (source: %s)",
            target_date,
            flow_data.get("source", "unknown"),
        )
    except Exception as e:
        session.rollback()
        logger.error("FII/DII store failed: %s", e)
    finally:
        session.close()
