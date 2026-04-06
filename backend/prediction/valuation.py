"""
Ultron Empire — Valuation Analysis
PE/PB percentile analysis and expected return estimation.
"""

import logging
import re
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)

# Historical Nifty 50 PE data (approximate distribution)
NIFTY_PE_HISTORY = {
    "mean": 20.5,
    "median": 20.0,
    "std": 4.5,
    "min": 10.7,   # March 2020
    "max": 38.6,   # Jan 2008
    "percentiles": {
        10: 15.5,
        25: 17.5,
        50: 20.0,
        75: 23.0,
        90: 27.0,
    },
}


def get_pe_percentile(current_pe: float) -> dict:
    """Get PE percentile and expected return implications."""
    history = NIFTY_PE_HISTORY

    # Calculate percentile
    if current_pe <= history["percentiles"][10]:
        percentile = 10
    elif current_pe <= history["percentiles"][25]:
        percentile = 25
    elif current_pe <= history["percentiles"][50]:
        percentile = 50
    elif current_pe <= history["percentiles"][75]:
        percentile = 75
    elif current_pe <= history["percentiles"][90]:
        percentile = 90
    else:
        percentile = 95

    # Expected 3Y forward returns based on PE zone
    if current_pe < 16:
        expected_3y_cagr = "18-25%"
        zone = "Deep Value"
        recommendation = "Aggressive deployment recommended"
    elif current_pe < 19:
        expected_3y_cagr = "14-20%"
        zone = "Value"
        recommendation = "Good time to deploy capital"
    elif current_pe < 22:
        expected_3y_cagr = "10-15%"
        zone = "Fair Value"
        recommendation = "Selective deployment via STP"
    elif current_pe < 25:
        expected_3y_cagr = "6-12%"
        zone = "Slightly Expensive"
        recommendation = "Cautious — prefer STP over lumpsum"
    else:
        expected_3y_cagr = "2-8%"
        zone = "Expensive"
        recommendation = "Avoid lumpsum. Deploy only via STP over 6-12 months"

    return {
        "current_pe": current_pe,
        "historical_mean": history["mean"],
        "percentile": percentile,
        "zone": zone,
        "expected_3y_cagr": expected_3y_cagr,
        "recommendation": recommendation,
        "deviation_from_mean": round(current_pe - history["mean"], 1),
    }


def get_live_nifty_pe() -> Optional[float]:
    """Try to fetch the current Nifty 50 PE ratio from live sources.

    Strategy:
    1. yfinance ticker(\"^NSEI\").info  — trailingPE or forwardPE
    2. Tavily search for \"Nifty 50 PE ratio today\"
    3. Return None so callers can fall back to their own default
    """
    # --- Attempt 1: yfinance ---
    try:
        import yfinance as yf

        ticker = yf.Ticker("^NSEI")
        info = ticker.info or {}
        pe = info.get("trailingPE") or info.get("forwardPE")
        if pe and isinstance(pe, (int, float)) and 5 < pe < 100:
            logger.info(f"Nifty PE from yfinance: {pe}")
            return round(float(pe), 2)
    except Exception as exc:
        logger.warning(f"yfinance PE fetch failed: {exc}")

    # --- Attempt 2: Tavily search ---
    try:
        from backend.config import settings
        from tavily import TavilyClient

        if settings.TAVILY_API_KEY:
            client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            response = client.search(
                query="Nifty 50 PE ratio today",
                search_depth="basic",
                max_results=3,
            )
            for result in response.get("results", []):
                content = result.get("content", "")
                # Look for PE-like numbers (e.g. "PE 22.5", "P/E: 21.3")
                matches = re.findall(r"(?:PE|P/E)[:\s]*(\d{1,2}\.\d{1,2})", content, re.IGNORECASE)
                if matches:
                    pe_val = float(matches[0])
                    if 5 < pe_val < 100:
                        logger.info(f"Nifty PE from Tavily: {pe_val}")
                        return round(pe_val, 2)
    except Exception as exc:
        logger.warning(f"Tavily PE fetch failed: {exc}")

    logger.info("Could not fetch live Nifty PE — returning None")
    return None
