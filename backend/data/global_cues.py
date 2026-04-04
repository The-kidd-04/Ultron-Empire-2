"""
Ultron Empire — Global Cues Pipeline
Fetches global macro indicators: Fed, crude, DXY, US yields, etc.
"""

import logging

logger = logging.getLogger(__name__)


def get_global_snapshot() -> dict:
    """Get comprehensive global macro snapshot."""
    try:
        import yfinance as yf

        tickers = {
            "sp500": {"symbol": "^GSPC", "name": "S&P 500"},
            "nasdaq": {"symbol": "^IXIC", "name": "Nasdaq"},
            "dow": {"symbol": "^DJI", "name": "Dow Jones"},
            "us_10y": {"symbol": "^TNX", "name": "US 10Y Yield"},
            "us_2y": {"symbol": "^IRX", "name": "US 2Y Yield"},
            "dxy": {"symbol": "DX-Y.NYB", "name": "Dollar Index"},
            "crude": {"symbol": "CL=F", "name": "Crude Oil (WTI)"},
            "brent": {"symbol": "BZ=F", "name": "Brent Crude"},
            "gold": {"symbol": "GC=F", "name": "Gold"},
            "silver": {"symbol": "SI=F", "name": "Silver"},
            "usdinr": {"symbol": "INR=X", "name": "USD/INR"},
            "btc": {"symbol": "BTC-USD", "name": "Bitcoin"},
        }

        result = {}
        for key, info in tickers.items():
            try:
                data = yf.Ticker(info["symbol"])
                hist = data.history(period="2d")
                if len(hist) >= 2:
                    close = round(hist.iloc[-1]["Close"], 2)
                    change = round(((hist.iloc[-1]["Close"] - hist.iloc[-2]["Close"]) / hist.iloc[-2]["Close"]) * 100, 2)
                    result[key] = {"name": info["name"], "value": close, "change_pct": change}
                elif len(hist) == 1:
                    result[key] = {"name": info["name"], "value": round(hist.iloc[-1]["Close"], 2), "change_pct": 0}
            except Exception:
                result[key] = {"name": info["name"], "value": "N/A", "change_pct": 0}

        return result
    except Exception as e:
        logger.error(f"Global snapshot failed: {e}")
        return {}


def format_global_cues(data: dict) -> str:
    """Format global cues for Telegram message."""
    if not data:
        return "Global data unavailable."

    lines = ["🌍 *Global Cues*\n"]
    for key in ["sp500", "nasdaq", "dxy", "us_10y", "crude", "gold", "usdinr"]:
        if key in data:
            d = data[key]
            lines.append(f"  {d['name']}: {d['value']} ({d['change_pct']:+.2f}%)")
    return "\n".join(lines)
