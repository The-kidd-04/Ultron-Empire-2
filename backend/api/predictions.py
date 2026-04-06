"""
Ultron Empire — Predictions API
GET /predictions — Market signals, momentum, patterns.
"""

from fastapi import APIRouter
from backend.prediction.momentum import (
    get_all_sector_momentum,
    calculate_momentum_score,
    compute_live_sector_momentum,
)
from backend.prediction.patterns import match_current_conditions
from backend.prediction.valuation import get_pe_percentile, get_live_nifty_pe
from backend.prediction.drawdown import estimate_drawdown_risk
from backend.prediction.monte_carlo import run_monte_carlo
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


@router.get("/momentum")
async def get_momentum():
    """Get latest sector momentum signals.

    If no signals exist in the database yet, automatically triggers a
    live computation via yfinance before returning.
    """
    signals = get_all_sector_momentum()
    if not signals:
        # No signals in DB — compute live and return fresh data
        live = compute_live_sector_momentum()
        return {s["sector"]: s for s in live}
    return signals


@router.get("/momentum/refresh")
async def refresh_momentum():
    """Force-refresh sector momentum signals from live market data."""
    results = compute_live_sector_momentum()
    return {"refreshed": len(results), "sectors": results}


@router.get("/patterns")
async def get_pattern_matches(
    nifty_pe: Optional[float] = None,
    vix: Optional[float] = None,
    fii_net_5d: Optional[float] = None,
    crude: Optional[float] = None,
):
    """Get pattern matches for current conditions."""
    matches = match_current_conditions(
        nifty_pe=nifty_pe, vix_level=vix,
        fii_net_5d=fii_net_5d, crude_price=crude,
    )
    return {"matches": matches, "count": len(matches)}


@router.get("/valuation")
async def get_valuation(pe: Optional[float] = None):
    """Get PE percentile analysis.

    If ``pe`` is not provided, attempts to fetch the live Nifty 50 PE
    ratio via yfinance / Tavily, falling back to 22.0.
    """
    if pe is None:
        pe = get_live_nifty_pe() or 22.0
    return get_pe_percentile(pe)


@router.get("/drawdown-risk")
async def get_drawdown(
    nifty_pe: float = 22.0,
    vix: float = 15.0,
    fii_net_monthly: float = -5000,
):
    """Get drawdown probability estimates."""
    return estimate_drawdown_risk(nifty_pe=nifty_pe, vix=vix, fii_net_monthly=fii_net_monthly)


class MonteCarloRequest(BaseModel):
    allocation: dict
    investment_cr: float
    horizon_years: int
    target_cr: Optional[float] = None


@router.post("/monte-carlo")
async def run_simulation(request: MonteCarloRequest):
    """Run Monte Carlo portfolio simulation."""
    return run_monte_carlo(
        allocation=request.allocation,
        investment_amount_cr=request.investment_cr,
        horizon_years=request.horizon_years,
        target_amount_cr=request.target_cr,
    )
