"""
Ultron Empire — Reports API
POST /reports — Generate client and market reports.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from backend.agents.analyst import chat_with_ultron

router = APIRouter()


class ReportRequest(BaseModel):
    report_type: str  # "client_portfolio", "fund_comparison", "market_outlook"
    client_name: Optional[str] = None
    fund_names: Optional[list] = None
    parameters: Optional[dict] = None


@router.post("")
async def generate_report(request: ReportRequest):
    """Generate a report based on type."""
    if request.report_type == "client_portfolio":
        if not request.client_name:
            return {"error": "client_name required"}
        result = await chat_with_ultron(
            f"Generate a comprehensive portfolio report for client {request.client_name}. "
            f"Include portfolio summary, performance analysis, risk assessment, "
            f"sector allocation, and recommendations."
        )
    elif request.report_type == "fund_comparison":
        if not request.fund_names or len(request.fund_names) < 2:
            return {"error": "At least 2 fund_names required"}
        funds = " vs ".join(request.fund_names)
        result = await chat_with_ultron(
            f"Generate a detailed comparison report for: {funds}. "
            f"Include returns, risk metrics, fees, holdings overlap, and recommendation."
        )
    elif request.report_type == "market_outlook":
        result = await chat_with_ultron(
            "Generate a comprehensive market outlook report. Include Nifty analysis, "
            "sector views, FII/DII trends, global factors, and investment strategy recommendations."
        )
    else:
        return {"error": f"Unknown report type: {request.report_type}"}

    return {
        "report_type": request.report_type,
        "content": result["response"],
        "tools_used": result["tools_used"],
    }
