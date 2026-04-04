"""
Ultron Empire — Sector Momentum Scoring System
Scores sectors from -100 to +100 based on multiple factors.
"""

import logging
from datetime import date
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
