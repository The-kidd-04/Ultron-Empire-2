"""
Ultron Empire — Currency Movement Impact (Feature 2.9)
Tracks USD/INR and analyzes impact on sectors and NRI clients.
"""

import logging

logger = logging.getLogger(__name__)


def get_currency_impact() -> dict:
    """Get USD/INR movement and sector impact analysis."""
    try:
        import yfinance as yf
        usdinr = yf.Ticker("INR=X")
        hist = usdinr.history(period="1mo")
        if len(hist) < 2:
            return {"error": "Currency data unavailable"}

        current = round(hist.iloc[-1]["Close"], 2)
        month_ago = round(hist.iloc[0]["Close"], 2)
        change_pct = round(((current - month_ago) / month_ago) * 100, 2)
        direction = "weakened" if change_pct > 0 else "strengthened"

        impact = {
            "IT Sector": "Positive" if change_pct > 0 else "Negative",
            "Pharma": "Positive" if change_pct > 0 else "Negative",
            "Import-Heavy (Auto, Oil)": "Negative" if change_pct > 0 else "Positive",
            "NRI Investments": f"Worth {'more' if change_pct > 0 else 'less'} in dollar terms",
        }

        return {
            "usdinr_current": current,
            "usdinr_month_ago": month_ago,
            "monthly_change_pct": change_pct,
            "rupee_direction": f"Rupee {direction} by {abs(change_pct)}% this month",
            "sector_impact": impact,
            "nri_alert": change_pct > 1.5,
            "alert_message": (
                f"Rupee {direction} {abs(change_pct)}% this month. "
                f"{'NRI clients investments worth more in dollar terms — good time for repatriation discussion.' if change_pct > 1.5 else ''}"
            ),
        }
    except Exception as e:
        logger.error(f"Currency tracker failed: {e}")
        return {"error": str(e)}
