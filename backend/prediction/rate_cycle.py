"""
Ultron Empire — Interest Rate Cycle Analysis
Tracks RBI rate cycle and its impact on sectors and asset classes.
"""

import logging

logger = logging.getLogger(__name__)

RATE_CYCLE_IMPACT = {
    "rate_cut": {
        "beneficiaries": ["Banking", "Realty", "Auto", "NBFCs", "Infrastructure"],
        "losers": ["Short-term Debt Funds"],
        "typical_nifty_impact": "+5 to +15% in 6-12 months",
        "pms_recommendation": "Shift to rate-sensitive PMS strategies",
    },
    "rate_hike": {
        "beneficiaries": ["IT (rupee depreciation)", "Pharma (defensive)", "FMCG"],
        "losers": ["Banking (NIM pressure)", "Realty", "Auto", "NBFCs"],
        "typical_nifty_impact": "-5 to 0% in 6-12 months",
        "pms_recommendation": "Prefer defensive large-cap PMS, increase debt AIF allocation",
    },
    "rate_pause": {
        "beneficiaries": ["Broad market — status quo"],
        "losers": ["Minimal"],
        "typical_nifty_impact": "0 to +10% (earnings-driven)",
        "pms_recommendation": "Stay with current allocation",
    },
}


def analyze_rate_cycle(
    current_repo_rate: float,
    last_action: str,  # "cut", "hike", "pause"
    inflation_cpi: float,
) -> dict:
    """Analyze current rate cycle position and implications.

    Args:
        current_repo_rate: Current RBI repo rate (e.g., 6.50)
        last_action: Last RBI action
        inflation_cpi: Current CPI inflation rate
    """
    real_rate = current_repo_rate - inflation_cpi
    cycle_data = RATE_CYCLE_IMPACT.get(f"rate_{last_action}", RATE_CYCLE_IMPACT["rate_pause"])

    # Predict next move
    if inflation_cpi < 4.0 and current_repo_rate > 6.0:
        next_likely = "cut"
        probability = 70
    elif inflation_cpi > 6.0:
        next_likely = "hike"
        probability = 65
    else:
        next_likely = "pause"
        probability = 60

    return {
        "repo_rate": current_repo_rate,
        "cpi_inflation": inflation_cpi,
        "real_rate": round(real_rate, 2),
        "last_action": last_action,
        "current_cycle": cycle_data,
        "next_likely_action": next_likely,
        "probability": probability,
        "sector_implications": cycle_data["beneficiaries"],
    }
