"""
Ultron Empire — Gifting Intelligence (Feature 4.9)
Ranks clients by AUM/trail and suggests gift budgets.
"""

import logging
from backend.db.database import SessionLocal
from backend.db.models import Client

logger = logging.getLogger(__name__)

GIFT_BUDGET_RULES = {
    "tier_1": {"min_aum": 10, "budget": 10000, "label": "Premium (₹10K+)"},
    "tier_2": {"min_aum": 5, "budget": 5000, "label": "Standard (₹5K)"},
    "tier_3": {"min_aum": 2, "budget": 3000, "label": "Basic (₹3K)"},
    "tier_4": {"min_aum": 0.5, "budget": 1500, "label": "Token (₹1.5K)"},
}


def generate_gifting_plan(occasion: str = "Diwali") -> dict:
    """Generate gifting plan ranked by client AUM."""
    session = SessionLocal()
    try:
        clients = session.query(Client).order_by(Client.current_aum_with_us.desc()).all()
        plan = []
        total_budget = 0

        for c in clients:
            aum = c.current_aum_with_us or 0
            if aum >= 10:
                tier = GIFT_BUDGET_RULES["tier_1"]
            elif aum >= 5:
                tier = GIFT_BUDGET_RULES["tier_2"]
            elif aum >= 2:
                tier = GIFT_BUDGET_RULES["tier_3"]
            elif aum >= 0.5:
                tier = GIFT_BUDGET_RULES["tier_4"]
            else:
                continue

            total_budget += tier["budget"]
            plan.append({
                "client": c.name,
                "aum_cr": aum,
                "tier": tier["label"],
                "budget_inr": tier["budget"],
                "estimated_annual_trail": round(aum * 75000, 0),  # ₹75K per Cr approx
            })

        return {
            "occasion": occasion,
            "total_clients": len(plan),
            "total_budget_inr": total_budget,
            "plan": plan,
            "note": f"Total {occasion} gifting budget: ₹{total_budget:,}",
        }
    finally:
        session.close()
