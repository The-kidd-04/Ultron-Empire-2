"""
Ultron Empire — Historical Pattern Matcher
Matches current market conditions against historical patterns.
"""

import logging
from datetime import date

logger = logging.getLogger(__name__)

PATTERNS = {
    "fii_selling_correction": {
        "name": "FII Selling → Market Correction",
        "description": "When FII selling exceeds ₹3000Cr/day for 5+ consecutive days",
        "historical_probability": 0.72,
        "typical_outcome": "Nifty correction of 3-8% within 2-4 weeks",
        "recovery_time": "4-8 weeks",
    },
    "vix_spike_bottom": {
        "name": "VIX Spike → Market Bottom",
        "description": "VIX above 25 for 3+ days often signals near-term bottom",
        "historical_probability": 0.65,
        "typical_outcome": "Market rebounds 5-12% within 1-3 months",
        "recovery_time": "1-3 months",
    },
    "pe_mean_reversion": {
        "name": "PE Mean Reversion",
        "description": "Nifty PE above 24 tends to revert to 20-21 average",
        "historical_probability": 0.78,
        "typical_outcome": "12-18 month returns muted when PE > 24",
        "recovery_time": "12-18 months",
    },
    "rate_cut_rotation": {
        "name": "Rate Cut Cycle → Sector Rotation",
        "description": "RBI rate cuts historically benefit Banking, Real Estate, Auto",
        "historical_probability": 0.70,
        "typical_outcome": "Rate-sensitive sectors outperform by 8-15%",
        "recovery_time": "6-12 months",
    },
    "crude_spike_impact": {
        "name": "Crude Oil Spike → OMC Impact",
        "description": "Crude above $85 pressures OMCs and auto sector",
        "historical_probability": 0.75,
        "typical_outcome": "OMC stocks decline 10-20%, auto margins compress",
        "recovery_time": "Until crude stabilizes",
    },
    "dii_buying_bottom": {
        "name": "DII Buying at Lows → Bottom Formation",
        "description": "DII buying > ₹5000Cr/day during corrections signals bottom",
        "historical_probability": 0.68,
        "typical_outcome": "Market forms bottom within 1-2 weeks",
        "recovery_time": "2-4 weeks",
    },
    "pre_election_rally": {
        "name": "Pre-Election Market Rally",
        "description": "Markets tend to rally 6-12 months before general elections",
        "historical_probability": 0.80,
        "typical_outcome": "Nifty rallies 15-25% in pre-election year",
        "recovery_time": "N/A",
    },
    "small_cap_correction_recovery": {
        "name": "Small Cap Correction Recovery",
        "description": "After 20%+ small cap correction, recovery within 12-18 months",
        "historical_probability": 0.85,
        "typical_outcome": "Small caps recover 30-50% from bottom",
        "recovery_time": "12-18 months",
    },
}


def match_current_conditions(
    nifty_pe: float = None,
    vix_level: float = None,
    fii_net_5d: float = None,
    crude_price: float = None,
    dii_net_today: float = None,
) -> list:
    """Match current conditions against known patterns."""
    matches = []

    if nifty_pe and nifty_pe > 24:
        p = PATTERNS["pe_mean_reversion"].copy()
        p["current_trigger"] = f"Nifty PE at {nifty_pe} (above 24 threshold)"
        matches.append(p)

    if vix_level and vix_level > 25:
        p = PATTERNS["vix_spike_bottom"].copy()
        p["current_trigger"] = f"VIX at {vix_level} (above 25 threshold)"
        matches.append(p)

    if fii_net_5d and fii_net_5d < -15000:  # ₹3000Cr/day * 5 days
        p = PATTERNS["fii_selling_correction"].copy()
        p["current_trigger"] = f"FII net selling ₹{abs(fii_net_5d)} Cr in 5 days"
        matches.append(p)

    if crude_price and crude_price > 85:
        p = PATTERNS["crude_spike_impact"].copy()
        p["current_trigger"] = f"Crude at ${crude_price} (above $85 threshold)"
        matches.append(p)

    if dii_net_today and dii_net_today > 5000:
        p = PATTERNS["dii_buying_bottom"].copy()
        p["current_trigger"] = f"DII bought ₹{dii_net_today} Cr today"
        matches.append(p)

    return matches
