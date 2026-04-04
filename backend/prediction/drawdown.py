"""
Ultron Empire — Drawdown Probability Model
Estimates drawdown risk based on current market conditions.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

HISTORICAL_DRAWDOWNS = {
    "2008_GFC": {"peak_to_trough": -52, "duration_months": 12, "recovery_months": 24},
    "2011_Euro_Crisis": {"peak_to_trough": -28, "duration_months": 6, "recovery_months": 14},
    "2015_China_Scare": {"peak_to_trough": -18, "duration_months": 4, "recovery_months": 8},
    "2018_NBFC_Crisis": {"peak_to_trough": -22, "duration_months": 10, "recovery_months": 18},
    "2020_COVID": {"peak_to_trough": -38, "duration_months": 2, "recovery_months": 12},
    "2022_Rate_Hike": {"peak_to_trough": -18, "duration_months": 8, "recovery_months": 10},
}


def estimate_drawdown_risk(
    nifty_pe: float,
    vix: float,
    fii_net_monthly: float,
) -> dict:
    """Estimate probability of various drawdown levels.

    Args:
        nifty_pe: Current Nifty PE ratio
        vix: Current India VIX level
        fii_net_monthly: FII net flow in current month (₹ Cr)
    """
    base_risk = 0.15  # Base 15% chance of >10% correction in any year

    # PE adjustment
    if nifty_pe > 25:
        pe_multiplier = 1.8
    elif nifty_pe > 22:
        pe_multiplier = 1.3
    elif nifty_pe > 20:
        pe_multiplier = 1.0
    else:
        pe_multiplier = 0.7

    # VIX adjustment
    if vix > 25:
        vix_multiplier = 1.5
    elif vix > 18:
        vix_multiplier = 1.2
    else:
        vix_multiplier = 0.8

    # FII flow adjustment
    if fii_net_monthly < -10000:
        fii_multiplier = 1.5
    elif fii_net_monthly < -5000:
        fii_multiplier = 1.2
    elif fii_net_monthly > 5000:
        fii_multiplier = 0.7
    else:
        fii_multiplier = 1.0

    adjusted_risk = base_risk * pe_multiplier * vix_multiplier * fii_multiplier
    adjusted_risk = min(adjusted_risk, 0.80)

    return {
        "probability_10pct_correction": round(adjusted_risk * 100, 1),
        "probability_20pct_correction": round(adjusted_risk * 50, 1),
        "probability_30pct_correction": round(adjusted_risk * 20, 1),
        "risk_level": "High" if adjusted_risk > 0.35 else "Moderate" if adjusted_risk > 0.20 else "Low",
        "factors": {
            "nifty_pe": nifty_pe,
            "pe_signal": "Elevated" if nifty_pe > 22 else "Fair",
            "vix": vix,
            "vix_signal": "High Fear" if vix > 25 else "Normal",
            "fii_monthly": fii_net_monthly,
            "fii_signal": "Heavy Selling" if fii_net_monthly < -10000 else "Normal",
        },
    }
