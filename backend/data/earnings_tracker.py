"""
Ultron Empire — Earnings Tracker
Tracks corporate earnings calendar and results for PMS-held stocks.
Uses yfinance for real earnings date lookups.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Common Indian stocks -> NSE tickers
# ---------------------------------------------------------------------------

STOCK_TICKER_MAP: dict[str, str] = {
    "HDFC Bank": "HDFCBANK.NS",
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Larsen & Toubro": "LT.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Axis Bank": "AXISBANK.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Sun Pharma": "SUNPHARMA.NS",
    "Titan Company": "TITAN.NS",
    "Wipro": "WIPRO.NS",
    "HCL Technologies": "HCLTECH.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "SBI": "SBIN.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "Power Grid": "POWERGRID.NS",
}


def _parse_earnings_date(raw) -> Optional[date]:
    """Attempt to extract a date from yfinance calendar data, which may vary in format."""
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw
    try:
        return datetime.strptime(str(raw)[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def get_upcoming_earnings(stocks: Optional[list[str]] = None) -> list[dict]:
    """Fetch upcoming earnings dates via yfinance Ticker.calendar.

    Parameters
    ----------
    stocks : list[str] | None
        List of stock names (keys in STOCK_TICKER_MAP). If None, checks all
        stocks in the map.

    Returns
    -------
    list[dict]
        Each dict has: stock, ticker, earnings_date (str|None), days_until (int|None).
    """
    try:
        import yfinance as yf
    except ImportError:
        logger.warning("yfinance is not installed — returning empty earnings calendar.")
        return []

    if stocks is None:
        stocks = list(STOCK_TICKER_MAP.keys())

    today = date.today()
    results: list[dict] = []

    for stock_name in stocks:
        ticker_symbol = STOCK_TICKER_MAP.get(stock_name)
        if ticker_symbol is None:
            logger.debug("No ticker mapping for '%s', skipping.", stock_name)
            continue

        earnings_date: Optional[date] = None
        try:
            ticker = yf.Ticker(ticker_symbol)
            cal = ticker.calendar
            if cal is not None:
                # yfinance returns calendar as a dict or DataFrame depending on version.
                if isinstance(cal, dict):
                    raw = cal.get("Earnings Date")
                    if isinstance(raw, list) and raw:
                        earnings_date = _parse_earnings_date(raw[0])
                    else:
                        earnings_date = _parse_earnings_date(raw)
                else:
                    # DataFrame path (older yfinance versions)
                    try:
                        raw = cal.loc["Earnings Date"].iloc[0]
                        earnings_date = _parse_earnings_date(raw)
                    except Exception:
                        pass
        except Exception as exc:
            logger.debug("Could not fetch calendar for %s (%s): %s", stock_name, ticker_symbol, exc)

        days_until: Optional[int] = None
        earnings_str: Optional[str] = None
        if earnings_date is not None:
            days_until = (earnings_date - today).days
            earnings_str = earnings_date.isoformat()

        results.append({
            "stock": stock_name,
            "ticker": ticker_symbol,
            "earnings_date": earnings_str,
            "days_until": days_until,
        })

    # Sort: stocks with known dates first (by date), then unknowns
    results.sort(key=lambda r: (r["days_until"] is None, r["days_until"] or 9999))
    return results


def get_earnings_for_portfolio(client_holdings: list[dict]) -> list[dict]:
    """Match client holdings to tickers and return upcoming earnings.

    Parameters
    ----------
    client_holdings : list[dict]
        Each dict should have a "product" key with the stock/product name.

    Returns
    -------
    list[dict]
        Upcoming earnings for matched stocks.
    """
    # Build a lookup of normalised name -> original name for fuzzy matching
    normalised_map: dict[str, str] = {}
    for name in STOCK_TICKER_MAP:
        normalised_map[name.lower()] = name

    matched_stocks: list[str] = []
    for holding in client_holdings:
        product = holding.get("product", "")
        product_lower = product.lower().strip()

        # Exact match
        if product_lower in normalised_map:
            matched_stocks.append(normalised_map[product_lower])
            continue

        # Substring match (e.g. "HDFC Bank Ltd" contains "HDFC Bank")
        for norm_name, orig_name in normalised_map.items():
            if norm_name in product_lower or product_lower in norm_name:
                matched_stocks.append(orig_name)
                break

    if not matched_stocks:
        return []

    return get_upcoming_earnings(stocks=list(set(matched_stocks)))


# ---------------------------------------------------------------------------
# Legacy functions (kept for backward compatibility)
# ---------------------------------------------------------------------------

def check_earnings_impact(stock: str, result_type: str, surprise_pct: float) -> dict:
    """Analyze earnings impact on PMS portfolios.

    Args:
        stock: Stock name (e.g., "HDFC Bank")
        result_type: "beat", "miss", or "inline"
        surprise_pct: Earnings surprise percentage
    """
    try:
        from backend.db.database import SessionLocal
        from backend.db.models import FundData
    except ImportError:
        return {
            "stock": stock,
            "result_type": result_type,
            "surprise_pct": surprise_pct,
            "affected_funds": [],
            "severity": "info",
        }

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
