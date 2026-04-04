"""
Ultron Empire — Portfolio Correlation Matrix
Analyzes correlations between fund holdings for diversification.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

# Pre-computed sector correlation matrix (approximate)
SECTOR_CORRELATIONS = {
    ("Banking", "Banking"): 1.0,
    ("Banking", "IT"): 0.35,
    ("Banking", "Pharma"): 0.20,
    ("Banking", "Auto"): 0.55,
    ("Banking", "FMCG"): 0.30,
    ("Banking", "Metal"): 0.40,
    ("Banking", "Realty"): 0.65,
    ("Banking", "Energy"): 0.45,
    ("IT", "IT"): 1.0,
    ("IT", "Pharma"): 0.25,
    ("IT", "Auto"): 0.30,
    ("IT", "FMCG"): 0.20,
    ("IT", "Metal"): 0.15,
    ("IT", "Realty"): 0.20,
    ("IT", "Energy"): 0.15,
    ("Pharma", "Pharma"): 1.0,
    ("Pharma", "Auto"): 0.15,
    ("Pharma", "FMCG"): 0.35,
    ("Metal", "Metal"): 1.0,
    ("Metal", "Energy"): 0.60,
    ("Realty", "Realty"): 1.0,
}


def get_sector_correlation(sector_a: str, sector_b: str) -> float:
    """Get correlation between two sectors."""
    if sector_a == sector_b:
        return 1.0
    key = (sector_a, sector_b)
    rev_key = (sector_b, sector_a)
    return SECTOR_CORRELATIONS.get(key, SECTOR_CORRELATIONS.get(rev_key, 0.30))


def analyze_portfolio_diversification(holdings: list) -> dict:
    """Analyze diversification quality of a portfolio.

    Args:
        holdings: List of dicts with 'sector_allocation' and 'weight'
    """
    # Aggregate sector exposures
    total_sectors = {}
    for h in holdings:
        weight = h.get("weight", 0) / 100
        for sector, pct in h.get("sector_allocation", {}).items():
            total_sectors[sector] = total_sectors.get(sector, 0) + (pct * weight)

    # Calculate concentration (HHI)
    total = sum(total_sectors.values())
    if total == 0:
        return {"error": "No sector data available"}

    normalized = {s: v / total * 100 for s, v in total_sectors.items()}
    hhi = sum((v / 100) ** 2 for v in normalized.values())

    # Diversification score (inverse of HHI, scaled to 100)
    div_score = round((1 - hhi) * 100, 1)

    return {
        "sector_exposure": {k: round(v, 1) for k, v in sorted(normalized.items(), key=lambda x: -x[1])},
        "hhi": round(hhi, 4),
        "diversification_score": div_score,
        "verdict": "Well Diversified" if div_score > 75 else "Moderately Diversified" if div_score > 55 else "Concentrated",
        "top_sector": max(normalized, key=normalized.get),
        "top_sector_weight": round(max(normalized.values()), 1),
    }
