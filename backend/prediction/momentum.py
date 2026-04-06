"""
Ultron Empire — Sector Momentum Scoring System
Scores sectors from -100 to +100 based on multiple factors.
"""

import logging
from datetime import date
from typing import List, Optional
from backend.db.database import SessionLocal
from backend.db.models import PredictionSignal

logger = logging.getLogger(__name__)


def calculate_momentum_score(
    above_50dma: bool,
    above_200dma: bool,
    rsi: float,
    fii_flow_trend: str,
    relative_strength: str,
) -> dict:
    """Calculate momentum score from -100 to +100.

    Weights:
    - Price vs 50-DMA: 25%
    - Price vs 200-DMA: 25%
    - RSI 14-day: 15%
    - FII/DII sector flow: 20%
    - Relative strength vs Nifty: 15%
    """
    score = 0

    # 50-DMA (25 points)
    score += 25 if above_50dma else -25

    # 200-DMA (25 points)
    score += 25 if above_200dma else -25

    # RSI (15 points): 30-70 is neutral, <30 oversold, >70 overbought
    if rsi < 30:
        score -= 10  # Oversold (contrarian positive but momentum negative)
    elif rsi > 70:
        score += 5  # Overbought (momentum positive but risky)
    elif 50 <= rsi <= 65:
        score += 15  # Healthy momentum
    elif 40 <= rsi < 50:
        score += 5  # Neutral-slight weakness
    else:
        score -= 5

    # FII flow trend (20 points)
    flow_scores = {"accumulating": 20, "neutral": 0, "distributing": -20}
    score += flow_scores.get(fii_flow_trend, 0)

    # Relative strength (15 points)
    rs_scores = {"outperforming": 15, "inline": 0, "underperforming": -15}
    score += rs_scores.get(relative_strength, 0)

    # Classify signal
    if score >= 50:
        signal, confidence = "Bullish", "High"
    elif score >= 20:
        signal, confidence = "Bullish", "Medium"
    elif score >= -20:
        signal, confidence = "Neutral", "Low"
    elif score >= -50:
        signal, confidence = "Bearish", "Medium"
    else:
        signal, confidence = "Bearish", "High"

    return {
        "score": max(-100, min(100, score)),
        "signal": signal,
        "confidence": confidence,
        "factors": {
            "above_50dma": above_50dma,
            "above_200dma": above_200dma,
            "rsi": rsi,
            "fii_flow_trend": fii_flow_trend,
            "relative_strength": relative_strength,
        },
    }


def store_momentum_signal(sector: str, momentum: dict):
    """Store momentum signal in database."""
    session = SessionLocal()
    try:
        signal = PredictionSignal(
            date=date.today(),
            signal_type="momentum",
            sector=sector,
            score=momentum["score"],
            signal=momentum["signal"],
            confidence=momentum["confidence"],
            factors=momentum["factors"],
            summary=f"{sector} momentum: {momentum['signal']} ({momentum['confidence']} confidence, score: {momentum['score']})",
        )
        session.add(signal)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Momentum signal store failed: {e}")
    finally:
        session.close()


def get_all_sector_momentum() -> dict:
    """Get latest momentum signals for all sectors."""
    session = SessionLocal()
    try:
        latest = (
            session.query(PredictionSignal)
            .filter(PredictionSignal.signal_type == "momentum")
            .order_by(PredictionSignal.date.desc())
            .limit(20)
            .all()
        )
        result = {}
        for s in latest:
            if s.sector not in result:
                result[s.sector] = {
                    "score": s.score,
                    "signal": s.signal,
                    "confidence": s.confidence,
                    "factors": s.factors,
                    "date": str(s.date),
                }
        return result
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Sector index tickers: (display_name, primary_ticker, fallback_ticker)
# ---------------------------------------------------------------------------
SECTOR_TICKERS = [
    ("Banking", "^NSEBANK", None),
    ("IT", "^CNXIT", None),
    ("Pharma", "^CNXPHARMA", "PHARMA.NS"),
    ("Auto", "^CNXAUTO", "AUTO.NS"),
    ("Realty", "^CNXREALTY", "REALTY.NS"),
    ("Metal", "^CNXMETAL", "METAL.NS"),
    ("FMCG", "^CNXFMCG", "FMCG.NS"),
    ("Energy", "^CNXENERGY", "ENERGY.NS"),
]

NIFTY_TICKER = "^NSEI"


def _fetch_sector_hist(ticker: str, fallback: Optional[str], period: str = "3mo"):
    """Fetch historical data via yfinance; try fallback ticker on failure."""
    import yfinance as yf

    try:
        data = yf.download(ticker, period=period, progress=False, threads=False)
        if data is not None and not data.empty:
            return data
    except Exception as exc:
        logger.warning(f"yfinance primary {ticker} failed: {exc}")

    if fallback:
        try:
            data = yf.download(fallback, period=period, progress=False, threads=False)
            if data is not None and not data.empty:
                return data
        except Exception as exc:
            logger.warning(f"yfinance fallback {fallback} failed: {exc}")

    return None


def _compute_rsi(closes, period: int = 14) -> float:
    """Calculate RSI-14 from a Series of closing prices."""
    import numpy as np

    deltas = closes.diff().dropna()
    gains = deltas.clip(lower=0)
    losses = (-deltas.clip(upper=0))

    avg_gain = gains.rolling(window=period, min_periods=period).mean().iloc[-1]
    avg_loss = losses.rolling(window=period, min_periods=period).mean().iloc[-1]

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return float(round(100 - (100 / (1 + rs)), 2))


def compute_live_sector_momentum() -> List[dict]:
    """Fetch live data via yfinance for all sectors and compute momentum signals.

    Returns a list of dicts, one per sector, each containing sector name and
    the full momentum result from ``calculate_momentum_score``.
    """
    import yfinance as yf

    # 1. Fetch Nifty 50 benchmark data for relative-strength comparison
    nifty_hist = _fetch_sector_hist(NIFTY_TICKER, fallback=None)
    if nifty_hist is not None and not nifty_hist.empty:
        nifty_close = nifty_hist["Close"].squeeze()
        nifty_return = float((nifty_close.iloc[-1] - nifty_close.iloc[0]) / nifty_close.iloc[0])
    else:
        nifty_return = 0.0
        logger.warning("Nifty 50 data unavailable — relative strength defaults to inline")

    results: List[dict] = []

    for sector_name, primary, fallback in SECTOR_TICKERS:
        try:
            hist = _fetch_sector_hist(primary, fallback)
            if hist is None or hist.empty:
                logger.warning(f"Skipping {sector_name}: no data available")
                continue

            close = hist["Close"].squeeze()
            if len(close) < 50:
                logger.warning(f"Skipping {sector_name}: insufficient data ({len(close)} rows)")
                continue

            current_price = float(close.iloc[-1])

            # 50-DMA & 200-DMA
            dma_50 = float(close.rolling(window=50, min_periods=50).mean().iloc[-1])
            above_50dma = current_price > dma_50

            if len(close) >= 200:
                dma_200 = float(close.rolling(window=200, min_periods=200).mean().iloc[-1])
            else:
                # Not enough data for true 200-DMA; use all available data
                dma_200 = float(close.mean())
            above_200dma = current_price > dma_200

            # RSI-14
            rsi = _compute_rsi(close, period=14)

            # Relative strength vs Nifty
            sector_return = float((close.iloc[-1] - close.iloc[0]) / close.iloc[0])
            diff = sector_return - nifty_return
            if diff > 0.02:
                relative_strength = "outperforming"
            elif diff < -0.02:
                relative_strength = "underperforming"
            else:
                relative_strength = "inline"

            # FII flow trend — not available from yfinance; default to neutral
            fii_flow_trend = "neutral"

            # Score & persist
            momentum = calculate_momentum_score(
                above_50dma=above_50dma,
                above_200dma=above_200dma,
                rsi=rsi,
                fii_flow_trend=fii_flow_trend,
                relative_strength=relative_strength,
            )
            store_momentum_signal(sector_name, momentum)

            results.append({
                "sector": sector_name,
                "score": momentum["score"],
                "signal": momentum["signal"],
                "confidence": momentum["confidence"],
                "factors": momentum["factors"],
                "date": str(date.today()),
            })

        except Exception as exc:
            logger.error(f"Momentum computation failed for {sector_name}: {exc}")
            continue

    return results
