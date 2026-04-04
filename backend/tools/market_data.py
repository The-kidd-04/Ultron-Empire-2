"""
Ultron Empire — Market Data Tool
Fetches current Indian market data using yfinance and NSE sources.
"""

from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)


def _safe_fetch_yfinance(ticker: str) -> dict:
    """Safely fetch data from yfinance."""
    try:
        import yfinance as yf
        data = yf.Ticker(ticker)
        hist = data.history(period="2d")
        if hist.empty:
            return {}
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else latest
        change_pct = ((latest["Close"] - prev["Close"]) / prev["Close"]) * 100
        return {
            "close": round(latest["Close"], 2),
            "change_pct": round(change_pct, 2),
            "high": round(latest["High"], 2),
            "low": round(latest["Low"], 2),
            "volume": int(latest["Volume"]),
        }
    except Exception as e:
        logger.warning(f"yfinance fetch failed for {ticker}: {e}")
        return {}


@tool
def market_data_tool(indicator: str = "overview") -> str:
    """Get current Indian market data and indicators.

    Args:
        indicator: What to fetch — "overview" (default, gets everything),
                   "nifty", "vix", "fii_dii", "sectors", "global",
                   "advance_decline", "pe_ratio"

    Returns:
        Current market data formatted as text.
    """
    sections = []

    if indicator in ("overview", "nifty"):
        nifty = _safe_fetch_yfinance("^NSEI")
        sensex = _safe_fetch_yfinance("^BSESN")
        if nifty:
            sections.append(
                f"🇮🇳 INDICES\n"
                f"Nifty 50: {nifty.get('close', 'N/A')} ({nifty.get('change_pct', 0):+.2f}%)\n"
                f"Sensex: {sensex.get('close', 'N/A')} ({sensex.get('change_pct', 0):+.2f}%)"
            )

    if indicator in ("overview", "vix"):
        vix = _safe_fetch_yfinance("^INDIAVIX")
        if vix:
            vix_val = vix.get("close", 0)
            vix_level = "Low" if vix_val < 14 else "Moderate" if vix_val < 20 else "Elevated" if vix_val < 25 else "High"
            sections.append(
                f"📊 VOLATILITY\n"
                f"India VIX: {vix_val} ({vix.get('change_pct', 0):+.2f}%) — {vix_level}"
            )

    if indicator in ("overview", "global"):
        global_tickers = {
            "S&P 500": "^GSPC",
            "Nasdaq": "^IXIC",
            "Crude Oil": "CL=F",
            "Gold": "GC=F",
            "Dollar Index": "DX-Y.NYB",
            "USD/INR": "INR=X",
        }
        global_data = []
        for name, ticker in global_tickers.items():
            data = _safe_fetch_yfinance(ticker)
            if data:
                global_data.append(f"  {name}: {data['close']} ({data['change_pct']:+.2f}%)")

        if global_data:
            sections.append("🌍 GLOBAL CUES\n" + "\n".join(global_data))

    if indicator in ("overview", "sectors"):
        sector_tickers = {
            "Bank Nifty": "^NSEBANK",
            "Nifty IT": "^CNXIT",
            "Nifty Pharma": "^CNXPHARMA",
            "Nifty Auto": "^CNXAUTO",
            "Nifty FMCG": "^CNXFMCG",
            "Nifty Metal": "^CNXMETAL",
            "Nifty Realty": "^CNXREALTY",
            "Nifty Energy": "^CNXENERGY",
        }
        sector_data = []
        for name, ticker in sector_tickers.items():
            data = _safe_fetch_yfinance(ticker)
            if data:
                sector_data.append(f"  {name}: {data['close']} ({data['change_pct']:+.2f}%)")

        if sector_data:
            sections.append("📈 SECTOR PERFORMANCE\n" + "\n".join(sector_data))

    if not sections:
        return "Unable to fetch market data. Please try again later."

    return "\n\n".join(sections)
