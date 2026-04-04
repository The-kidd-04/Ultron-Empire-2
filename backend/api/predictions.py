"""
Ultron Empire — Predictions API
GET /predictions — Market signals, momentum, patterns.
"""

from fastapi import APIRouter
from backend.prediction.momentum import get_all_sector_momentum, calculate_momentum_score
from backend.prediction.patterns import match_current_conditions
from backend.prediction.valuation import get_pe_percentile
from backend.prediction.drawdown import estimate_drawdown_risk
from backend.prediction.monte_carlo import run_monte_carlo
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


@router.get("/momentum")
async def get_momentum():
    """Get latest sector momentum signals."""
    return get_all_sector_momentum()


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
async def get_valuation(pe: float = 22.0):
    """Get PE percentile analysis."""
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
