"""
Ultron Empire — Commission & Trail Income Forecasting
Predicts revenue from current AUM and client pipeline.
"""

import logging

logger = logging.getLogger(__name__)

# Approximate trail income rates
TRAIL_RATES = {
    "PMS": 0.0075,       # 0.75% average trail on PMS
    "AIF_Cat2": 0.005,   # 0.5% on AIF Cat II
    "AIF_Cat3": 0.005,   # 0.5% on AIF Cat III
    "AIF_Cat1": 0.005,   # 0.5% on AIF Cat I
    "MF_Regular": 0.01,  # 1% on regular MF
    "MF_Direct": 0,      # 0% on direct MF
}


def forecast_trail_income(holdings: list) -> dict:
    """Forecast annual trail income from client holdings.

    Args:
        holdings: List of {"product": "...", "amount": X, "type": "PMS"/"AIF"/etc}
    """
    total_trail = 0
    breakdown = []

    for h in holdings:
        product = h.get("product", "")
        amount = h.get("amount", 0)
        ptype = h.get("type", "PMS")

        rate = TRAIL_RATES.get(ptype, 0.0075)
        trail = amount * rate

        total_trail += trail
        breakdown.append({
            "product": product,
            "aum_cr": amount,
            "trail_rate": f"{rate*100:.2f}%",
            "annual_trail_cr": round(trail, 4),
        })

    return {
        "total_annual_trail_cr": round(total_trail, 4),
        "total_monthly_trail_cr": round(total_trail / 12, 4),
        "breakdown": sorted(breakdown, key=lambda x: -x["annual_trail_cr"]),
    }


def project_revenue(current_aum_cr: float, growth_rate_pct: float = 15, years: int = 3) -> dict:
    """Project future revenue based on AUM growth."""
    projections = []
    aum = current_aum_cr

    for year in range(1, years + 1):
        aum *= (1 + growth_rate_pct / 100)
        trail = aum * 0.0075  # Average trail
        projections.append({
            "year": year,
            "projected_aum_cr": round(aum, 2),
            "projected_annual_trail_cr": round(trail, 4),
            "projected_monthly_trail_cr": round(trail / 12, 4),
        })

    return {
        "current_aum_cr": current_aum_cr,
        "growth_assumption": f"{growth_rate_pct}% per year",
        "projections": projections,
    }
