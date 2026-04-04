"""
Ultron Empire — Fund Manager Behavior Analysis (Feature 3.2)
Analyzes how PMS managers historically react during corrections.
"""

import logging

logger = logging.getLogger(__name__)

# Pre-analyzed fund manager behavior patterns (from NAV analysis)
MANAGER_BEHAVIORS = {
    "Sandeep Tandon": {
        "fund": "Quant Small Cap PMS",
        "style": "Momentum + Quantitative",
        "correction_behavior": "Reduces exposure quickly, holds 15-20% cash in downturns",
        "recovery_speed": "Fast — typically among first to recover",
        "cash_in_corrections": "15-20%",
        "conviction_level": "High turnover — adapts quickly",
    },
    "Amit Jeswani": {
        "fund": "Stallion Asset Core PMS",
        "style": "Growth at Reasonable Price",
        "correction_behavior": "Stays fully invested, rarely holds cash",
        "recovery_speed": "Moderate — relies on stock quality for recovery",
        "cash_in_corrections": "0-5%",
        "conviction_level": "Very high — low turnover, long holding periods",
    },
    "Saurabh Mukherjea": {
        "fund": "Marcellus CCP",
        "style": "Quality Compounding",
        "correction_behavior": "Fully invested always. Believes quality compounds through cycles",
        "recovery_speed": "Slow but steady — lower drawdown than peers",
        "cash_in_corrections": "0-2%",
        "conviction_level": "Extremely high — <10% annual turnover",
    },
    "Hiren Ved": {
        "fund": "Alchemy High Growth PMS",
        "style": "Growth-oriented Mid Cap",
        "correction_behavior": "Moderate trimming, increases quality tilt",
        "recovery_speed": "Good — active management helps",
        "cash_in_corrections": "5-10%",
        "conviction_level": "Moderate — adjusts positions tactically",
    },
    "Sunil Singhania": {
        "fund": "Abakkus All Cap Approach PMS",
        "style": "All-cap value + growth blend",
        "correction_behavior": "Uses corrections to add quality names at discount",
        "recovery_speed": "Fast — aggressive buying at lows pays off",
        "cash_in_corrections": "10-15% pre-correction, deploys during dip",
        "conviction_level": "High — experienced across market cycles",
    },
}


def get_manager_analysis(fund_name: str = None, manager_name: str = None) -> dict:
    """Get fund manager behavior analysis during corrections."""
    if manager_name:
        behavior = MANAGER_BEHAVIORS.get(manager_name)
        if behavior:
            return behavior
    if fund_name:
        for manager, data in MANAGER_BEHAVIORS.items():
            if fund_name.lower() in data["fund"].lower():
                return {**data, "manager": manager}

    return {
        "all_managers": list(MANAGER_BEHAVIORS.keys()),
        "note": "Specify fund_name or manager_name for detailed analysis",
    }


def compare_manager_behaviors(managers: list) -> list:
    """Compare how multiple managers behave during corrections."""
    results = []
    for m in managers:
        if m in MANAGER_BEHAVIORS:
            results.append({"manager": m, **MANAGER_BEHAVIORS[m]})
    return results
