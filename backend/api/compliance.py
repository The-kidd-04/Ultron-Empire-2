"""
Ultron Empire — Compliance API
POST /compliance/* — SEBI compliance checking endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from backend.compliance.sebi_rules import (
    check_pms_compliance,
    check_aif_compliance,
    check_client_suitability,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class PMSCheckRequest(BaseModel):
    investment_amount_lakhs: float = Field(..., description="Investment amount in lakhs")
    fee_fixed_pct: float = Field(0.0, description="Fixed management fee percentage")
    fee_perf_pct: float = Field(0.0, description="Performance fee percentage")
    has_disclosure: bool = Field(True, description="Whether fee disclosure has been provided")
    has_monthly_reporting: bool = Field(True, description="Whether monthly reporting is set up")


class AIFCheckRequest(BaseModel):
    category: str = Field(..., description="AIF category: I, II, or III")
    investment_amount_cr: float = Field(..., description="Investment amount in crores")
    investor_count: int = Field(1, description="Number of investors in the scheme")
    lock_in_years: float = Field(3.0, description="Lock-in period in years")
    leverage_ratio: float = Field(1.0, description="Leverage ratio (1.0 = no leverage)")


class SuitabilityCheckRequest(BaseModel):
    client_risk_profile: str = Field(..., description="Client risk profile: conservative, moderate, aggressive")
    product_category: str = Field(..., description="Product category, e.g. 'AIF Cat III', 'Small Cap PMS'")
    investment_pct_of_wealth: float = Field(..., description="Percentage of total wealth allocated (0-100)")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/check-pms")
async def api_check_pms(req: PMSCheckRequest):
    """Validate a PMS investment against SEBI regulations."""
    return check_pms_compliance(
        investment_amount_lakhs=req.investment_amount_lakhs,
        fee_fixed_pct=req.fee_fixed_pct,
        fee_perf_pct=req.fee_perf_pct,
        has_disclosure=req.has_disclosure,
        has_monthly_reporting=req.has_monthly_reporting,
    )


@router.post("/check-aif")
async def api_check_aif(req: AIFCheckRequest):
    """Validate an AIF investment against SEBI regulations."""
    return check_aif_compliance(
        category=req.category,
        investment_amount_cr=req.investment_amount_cr,
        investor_count=req.investor_count,
        lock_in_years=req.lock_in_years,
        leverage_ratio=req.leverage_ratio,
    )


@router.post("/check-suitability")
async def api_check_suitability(req: SuitabilityCheckRequest):
    """Validate product suitability for a client's risk profile."""
    return check_client_suitability(
        client_risk_profile=req.client_risk_profile,
        product_category=req.product_category,
        investment_pct_of_wealth=req.investment_pct_of_wealth,
    )
