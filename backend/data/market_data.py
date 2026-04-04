"""
Ultron Empire — Market Data Pipeline
Fetches real-time and historical data from NSE/BSE via yfinance.
"""

import logging
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)


def get_nifty_data() -> dict:
    """Get current Nifty 50 data."""
    try:
        import yfinance as yf
        nifty = yf.Ticker("^NSEI")
        hist = nifty.history(period="2d")
        if hist.empty:
            return {"close": "N/A", "change_pct": 0, "pe_ratio": "N/A"}
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else latest
        change_pct = ((latest["Close"] - prev["Close"]) / prev["Close"]) * 100

        sensex = yf.Ticker("^BSESN")
        sensex_hist = sensex.history(period="2d")
        sensex_close = sensex_hist.iloc[-1]["Close"] if not sensex_hist.empty else "N/A"
        sensex_change = ((sensex_hist.iloc[-1]["Close"] - sensex_hist.iloc[-2]["Close"]) / sensex_hist.iloc[-2]["Close"]) * 100 if len(sensex_hist) > 1 else 0

        return {
            "close": round(latest["Close"], 2),
            "change_pct": round(change_pct, 2),
            "high": round(latest["High"], 2),
            "low": round(latest["Low"], 2),
            "volume": int(latest["Volume"]),
            "sensex_close": round(sensex_close, 2) if isinstance(sensex_close, float) else sensex_close,
            "sensex_change_pct": round(sensex_change, 2),
            "pe_ratio": "N/A",  # PE requires separate source
        }
    except Exception as e:
        logger.error(f"Nifty data fetch failed: {e}")
        return {"close": "N/A", "change_pct": 0}


def get_vix() -> dict:
    """Get India VIX data."""
    try:
        import yfinance as yf
        vix = yf.Ticker("^INDIAVIX")
        hist = vix.history(period="2d")
        if hist.empty:
            return {"value": "N/A", "change_pct": 0}
        latest = hist.iloc[-1]["Close"]
        prev = hist.iloc[-2]["Close"] if len(hist) > 1 else latest
        change = ((latest - prev) / prev) * 100
        return {"value": round(latest, 2), "change_pct": round(change, 2)}
    except Exception as e:
        logger.error(f"VIX fetch failed: {e}")
        return {"value": "N/A", "change_pct": 0}


def get_fii_dii() -> dict:
    """Get FII/DII flow data. In production: scrape NSE website."""
    return {
        "fii_net": "N/A",
        "fii_direction": "N/A",
        "dii_net": "N/A",
        "dii_direction": "N/A",
        "note": "FII/DII data requires NSE scraper integration",
    }


def get_sector_indices() -> list:
    """Get sector index performance."""
    import yfinance as yf
    sectors = {
        "Bank Nifty": "^NSEBANK",
        "Nifty IT": "^CNXIT",
        "Nifty Pharma": "^CNXPHARMA",
        "Nifty Auto": "^CNXAUTO",
        "Nifty FMCG": "^CNXFMCG",
        "Nifty Metal": "^CNXMETAL",
        "Nifty Realty": "^CNXREALTY",
        "Nifty Energy": "^CNXENERGY",
    }
    results = []
    for name, ticker in sectors.items():
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="2d")
            if len(hist) >= 2:
                change = ((hist.iloc[-1]["Close"] - hist.iloc[-2]["Close"]) / hist.iloc[-2]["Close"]) * 100
                results.append({"name": name, "close": round(hist.iloc[-1]["Close"], 2), "change_pct": round(change, 2)})
        except Exception:
            continue
    return results


def get_global_cues() -> dict:
    """Get global market indicators."""
    import yfinance as yf
    tickers = {"us_10y": "^TNX", "dxy": "DX-Y.NYB", "crude": "CL=F", "gold": "GC=F"}
    result = {}
    for key, ticker in tickers.items():
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="1d")
            if not hist.empty:
                result[key] = round(hist.iloc[-1]["Close"], 2)
        except Exception:
            result[key] = "N/A"
    return result


def get_market_snapshot() -> str:
    """Get a formatted market snapshot string."""
    nifty = get_nifty_data()
    vix = get_vix()
    sectors = get_sector_indices()
    global_cues = get_global_cues()

    sector_text = "\n".join(f"  {s['name']}: {s['close']} ({s['change_pct']:+.2f}%)" for s in sectors)

    return (
        f"🇮🇳 *Market Snapshot*\n\n"
        f"Nifty 50: {nifty.get('close', 'N/A')} ({nifty.get('change_pct', 0):+.2f}%)\n"
        f"Sensex: {nifty.get('sensex_close', 'N/A')} ({nifty.get('sensex_change_pct', 0):+.2f}%)\n"
        f"India VIX: {vix.get('value', 'N/A')} ({vix.get('change_pct', 0):+.2f}%)\n\n"
        f"📈 *Sectors*\n{sector_text}\n\n"
        f"🌍 *Global*\n"
        f"  US 10Y: {global_cues.get('us_10y', 'N/A')}%\n"
        f"  DXY: {global_cues.get('dxy', 'N/A')}\n"
        f"  Crude: ${global_cues.get('crude', 'N/A')}\n"
        f"  Gold: ${global_cues.get('gold', 'N/A')}"
    )
