"""
Ultron Empire — Sector Data Pipeline
Sector indices, rotation analysis, and relative strength.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

SECTOR_TICKERS = {
    "Banking": "^NSEBANK",
    "IT": "^CNXIT",
    "Pharma": "^CNXPHARMA",
    "Auto": "^CNXAUTO",
    "FMCG": "^CNXFMCG",
    "Metal": "^CNXMETAL",
    "Realty": "^CNXREALTY",
    "Energy": "^CNXENERGY",
}


def get_sector_performance(period: str = "1mo") -> list:
    """Get sector-wise performance for a given period."""
    try:
        import yfinance as yf
        results = []
        for name, ticker in SECTOR_TICKERS.items():
            try:
                data = yf.Ticker(ticker)
                hist = data.history(period=period)
                if len(hist) >= 2:
                    start_price = hist.iloc[0]["Close"]
                    end_price = hist.iloc[-1]["Close"]
                    change_pct = ((end_price - start_price) / start_price) * 100
                    results.append({
                        "sector": name,
                        "current": round(end_price, 2),
                        "change_pct": round(change_pct, 2),
                        "high": round(hist["High"].max(), 2),
                        "low": round(hist["Low"].min(), 2),
                    })
            except Exception:
                continue
        return sorted(results, key=lambda x: x["change_pct"], reverse=True)
    except Exception as e:
        logger.error(f"Sector performance fetch failed: {e}")
        return []


def identify_sector_rotation(short_period: str = "1mo", long_period: str = "3mo") -> dict:
    """Identify sector rotation by comparing short and long term performance."""
    short = {s["sector"]: s["change_pct"] for s in get_sector_performance(short_period)}
    long = {s["sector"]: s["change_pct"] for s in get_sector_performance(long_period)}

    rotation = {}
    for sector in short:
        if sector in long:
            momentum_shift = short[sector] - (long[sector] / 3)  # Normalize 3M to monthly
            rotation[sector] = {
                "short_term": short[sector],
                "long_term": long[sector],
                "momentum_shift": round(momentum_shift, 2),
                "signal": "Improving" if momentum_shift > 2 else "Weakening" if momentum_shift < -2 else "Stable",
            }
    return rotation
