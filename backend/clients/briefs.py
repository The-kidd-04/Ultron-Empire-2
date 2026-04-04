"""
Ultron Empire — Pre-Meeting Client Brief Generator
"""

import logging
from backend.db.database import SessionLocal
from backend.db.models import Client, FundData, Alert

logger = logging.getLogger(__name__)


def generate_client_brief(client_name: str) -> dict:
    """Generate a pre-meeting brief for a client."""
    session = SessionLocal()
    try:
        client = session.query(Client).filter(Client.name.ilike(f"%{client_name}%")).first()
        if not client:
            return {"error": f"Client '{client_name}' not found"}

        holdings = client.holdings or []
        total_aum = sum(h.get("amount", 0) for h in holdings)

        # Get fund performance for holdings
        holding_details = []
        for h in holdings:
            fund = session.query(FundData).filter(
                FundData.fund_name.ilike(f"%{h['product']}%")
            ).first()
            holding_details.append({
                "product": h["product"],
                "amount_cr": h["amount"],
                "since": h.get("date", "N/A"),
                "returns_1y": fund.returns_1y if fund else None,
                "max_drawdown": fund.max_drawdown if fund else None,
            })

        # Recent alerts for this client
        recent_alerts = (
            session.query(Alert)
            .filter(Alert.client_id == client.id)
            .order_by(Alert.created_at.desc())
            .limit(5)
            .all()
        )

        # Talking points
        talking_points = []
        if client.next_review_date:
            talking_points.append(f"Review scheduled: {client.next_review_date}")

        for h in holding_details:
            if h["returns_1y"] and h["returns_1y"] > 30:
                talking_points.append(f"🟢 {h['product']} up {h['returns_1y']}% — discuss profit booking?")
            elif h["returns_1y"] and h["returns_1y"] < 5:
                talking_points.append(f"🔴 {h['product']} underperforming at {h['returns_1y']}% — explain thesis")

        if client.goals:
            for g in client.goals:
                talking_points.append(f"Goal: {g['name']} — ₹{g['target']} Cr in {g['years']} years")

        return {
            "client": {
                "name": client.name,
                "age": client.age,
                "occupation": client.occupation,
                "city": client.city,
                "risk_profile": client.risk_profile,
                "investment_horizon": client.investment_horizon,
            },
            "aum_with_us": total_aum,
            "total_wealth": client.total_investable_wealth,
            "holdings": holding_details,
            "goals": client.goals,
            "family": client.family_members,
            "recent_alerts": [{"title": a.title, "priority": a.priority} for a in recent_alerts],
            "talking_points": talking_points,
            "notes": client.notes,
            "communication_preference": client.communication_preference,
        }
    finally:
        session.close()
