"""
Ultron Empire — Client Onboarding Graph (LangGraph)
Guided workflow for onboarding new clients.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
import logging

logger = logging.getLogger(__name__)


class OnboardingState(TypedDict):
    client_name: str
    age: Optional[int]
    wealth_cr: Optional[float]
    risk_profile: Optional[str]
    goals: Optional[list]
    risk_assessment: str
    recommended_allocation: dict
    recommended_funds: list
    onboarding_summary: str


async def assess_risk(state: OnboardingState) -> dict:
    """Assess client risk profile based on inputs."""
    age = state.get("age", 40)
    wealth = state.get("wealth_cr", 1)

    if state.get("risk_profile"):
        profile = state["risk_profile"]
    elif age > 55:
        profile = "Conservative"
    elif age > 40:
        profile = "Moderate"
    else:
        profile = "Aggressive"

    assessment = (
        f"Risk Assessment for {state['client_name']}:\n"
        f"Age: {age} | Wealth: ₹{wealth} Cr\n"
        f"Assessed Profile: {profile}\n"
    )
    return {"risk_assessment": assessment, "risk_profile": profile}


async def generate_allocation(state: OnboardingState) -> dict:
    """Generate recommended asset allocation."""
    profile = state.get("risk_profile", "Moderate")

    allocations = {
        "Conservative": {"Large Cap PMS": 40, "Debt AIF": 35, "Fixed Income": 25},
        "Moderate": {"Multi Cap PMS": 35, "Mid Cap PMS": 25, "Debt AIF": 20, "Large Cap PMS": 20},
        "Aggressive": {"Small Cap PMS": 30, "Mid Cap PMS": 25, "Multi Cap PMS": 25, "Cat III AIF": 20},
    }
    return {"recommended_allocation": allocations.get(profile, allocations["Moderate"])}


async def select_funds(state: OnboardingState) -> dict:
    """Select specific funds based on allocation."""
    from backend.db.database import SessionLocal
    from backend.db.models import FundData

    session = SessionLocal()
    try:
        recommendations = []
        for asset_class, weight in state.get("recommended_allocation", {}).items():
            strategy_map = {
                "Large Cap PMS": "Large Cap",
                "Multi Cap PMS": "Multi Cap",
                "Mid Cap PMS": "Mid Cap",
                "Small Cap PMS": "Small Cap",
                "Flexi Cap PMS": "Flexi Cap",
            }
            strategy = strategy_map.get(asset_class)
            if strategy:
                funds = session.query(FundData).filter(
                    FundData.strategy == strategy, FundData.category == "PMS"
                ).order_by(FundData.sharpe_ratio.desc()).limit(3).all()

                for f in funds:
                    recommendations.append({
                        "fund": f.fund_name,
                        "house": f.fund_house,
                        "strategy": f.strategy,
                        "allocation_pct": weight,
                        "returns_1y": f.returns_1y,
                        "sharpe": f.sharpe_ratio,
                    })

        return {"recommended_funds": recommendations}
    finally:
        session.close()


async def generate_summary(state: OnboardingState) -> dict:
    """Generate onboarding summary."""
    funds_text = "\n".join(
        f"  • {f['fund']} ({f['strategy']}): {f['allocation_pct']}% — 1Y: {f.get('returns_1y', 'N/A')}%"
        for f in state.get("recommended_funds", [])
    )

    summary = (
        f"📋 *Onboarding Summary: {state['client_name']}*\n\n"
        f"{state.get('risk_assessment', '')}\n"
        f"📊 *Recommended Allocation:*\n"
        + "\n".join(f"  {k}: {v}%" for k, v in state.get("recommended_allocation", {}).items())
        + f"\n\n📈 *Recommended Funds:*\n{funds_text}\n\n"
        f"_Next steps: Schedule detailed discussion, KYC, and investment execution._"
    )
    return {"onboarding_summary": summary}


def build_onboarding_graph():
    graph = StateGraph(OnboardingState)
    graph.add_node("assess_risk", assess_risk)
    graph.add_node("generate_allocation", generate_allocation)
    graph.add_node("select_funds", select_funds)
    graph.add_node("generate_summary", generate_summary)

    graph.set_entry_point("assess_risk")
    graph.add_edge("assess_risk", "generate_allocation")
    graph.add_edge("generate_allocation", "select_funds")
    graph.add_edge("select_funds", "generate_summary")
    graph.add_edge("generate_summary", END)

    return graph.compile()


onboarding_pipeline = build_onboarding_graph()
