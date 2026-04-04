"""
Ultron Empire — Analytics API
GET /analytics — Business metrics and revenue forecasting.
"""

from fastapi import APIRouter
from backend.analytics.business_metrics import get_business_dashboard, get_growth_metrics
from backend.analytics.commission_forecast import project_revenue

router = APIRouter()


@router.get("")
async def get_analytics():
    """Get full business analytics dashboard."""
    return get_business_dashboard()


@router.get("/growth")
async def get_growth():
    """Get client growth metrics."""
    return get_growth_metrics()


@router.get("/forecast")
async def get_forecast(current_aum: float = 12.0, growth_rate: float = 15, years: int = 3):
    """Project future revenue."""
    return project_revenue(current_aum, growth_rate, years)
