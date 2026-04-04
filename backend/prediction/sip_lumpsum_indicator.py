"""
Ultron Empire — SIP vs Lumpsum Timing Indicator (Feature 1.10)
Combines PE percentile + VIX to suggest deployment strategy.
"""

import logging
from backend.prediction.valuation import get_pe_percentile

logger = logging.getLogger(__name__)

# Historical data: lumpsum vs SIP outperformance at different PE levels
PE_LUMPSUM_WIN_RATE = {
    "below_16": 85,   # Deep value — lumpsum almost always wins
    "16_to_19": 72,
    "19_to_22": 60,
    "22_to_25": 48,   # Coin flip territory
    "above_25": 35,   # Expensive — SIP usually wins
}


def get_deployment_recommendation(nifty_pe: float, vix: float, amount_cr: float = 1.0) -> dict:
    """Get SIP vs lumpsum recommendation based on current conditions.

    Args:
        nifty_pe: Current Nifty PE ratio
        vix: Current India VIX level
        amount_cr: Amount to deploy in crores
    """
    pe_analysis = get_pe_percentile(nifty_pe)

    # PE-based lumpsum win rate
    if nifty_pe < 16:
        lumpsum_win_rate = PE_LUMPSUM_WIN_RATE["below_16"]
    elif nifty_pe < 19:
        lumpsum_win_rate = PE_LUMPSUM_WIN_RATE["16_to_19"]
    elif nifty_pe < 22:
        lumpsum_win_rate = PE_LUMPSUM_WIN_RATE["19_to_22"]
    elif nifty_pe < 25:
        lumpsum_win_rate = PE_LUMPSUM_WIN_RATE["22_to_25"]
    else:
        lumpsum_win_rate = PE_LUMPSUM_WIN_RATE["above_25"]

    # VIX adjustment
    if vix > 25:
        vix_signal = "High fear — near-term volatility likely"
        vix_adjustment = -15  # Reduce lumpsum preference
    elif vix > 18:
        vix_signal = "Elevated — moderate caution"
        vix_adjustment = -5
    elif vix < 12:
        vix_signal = "Complacent — contrarian caution"
        vix_adjustment = -5
    else:
        vix_signal = "Normal range"
        vix_adjustment = 0

    adjusted_rate = max(10, min(90, lumpsum_win_rate + vix_adjustment))

    # Generate recommendation
    if adjusted_rate >= 70:
        strategy = "Lumpsum"
        split = {"lumpsum": 80, "stp": 20}
        reasoning = f"At PE {nifty_pe} with VIX {vix}, markets are attractively valued. Deploy majority now."
    elif adjusted_rate >= 55:
        strategy = "Hybrid"
        split = {"lumpsum": 50, "stp": 50}
        reasoning = f"Markets fairly valued. Split deployment — ₹{amount_cr*0.5:.1f} Cr now, rest via STP over 3-6 months."
    elif adjusted_rate >= 40:
        strategy = "STP-Heavy"
        split = {"lumpsum": 30, "stp": 70}
        reasoning = f"Markets moderately expensive. Deploy ₹{amount_cr*0.3:.1f} Cr now, STP the rest over 6 months."
    else:
        strategy = "Full STP"
        split = {"lumpsum": 10, "stp": 90}
        reasoning = f"Markets expensive at PE {nifty_pe}. Deploy via STP over 6-12 months to average out."

    return {
        "nifty_pe": nifty_pe,
        "pe_percentile": pe_analysis["percentile"],
        "pe_zone": pe_analysis["zone"],
        "vix": vix,
        "vix_signal": vix_signal,
        "lumpsum_historical_win_rate": f"{lumpsum_win_rate}%",
        "adjusted_win_rate": f"{adjusted_rate}%",
        "recommended_strategy": strategy,
        "suggested_split": split,
        "reasoning": reasoning,
        "for_amount": f"₹{amount_cr} Cr",
    }
