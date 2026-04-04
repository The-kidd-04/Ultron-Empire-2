"""
Ultron Empire — Client Lookup Tool
Search client profiles and portfolio details from CRM.
"""

from langchain_core.tools import tool
from backend.db.database import SessionLocal
from backend.db.models import Client
import logging

logger = logging.getLogger(__name__)


@tool
def client_lookup_tool(name: str = None, client_id: int = None) -> str:
    """Look up client profiles and portfolio details.

    Args:
        name: Client name (partial match supported)
        client_id: Client ID for exact lookup

    Returns:
        Client profile with holdings, goals, and review status.
    """
    session = SessionLocal()
    try:
        if client_id:
            client = session.query(Client).get(client_id)
        elif name:
            client = session.query(Client).filter(
                Client.name.ilike(f"%{name}%")
            ).first()
        else:
            return "Please provide a client name or ID."

        if not client:
            return f"No client found matching '{name or client_id}'."

        holdings = client.holdings or []
        holdings_text = "\n".join(
            f"  • {h['product']}: ₹{h['amount']} Cr (since {h['date']})"
            for h in holdings
        ) or "  No holdings recorded"

        goals = client.goals or []
        goals_text = "\n".join(
            f"  • {g['name']}: ₹{g['target']} Cr in {g['years']} years"
            for g in goals
        ) or "  No goals recorded"

        family = client.family_members or []
        family_text = "\n".join(
            f"  • {f['name']} ({f['relation']}, age {f['age']})"
            for f in family
        ) or "  No family members recorded"

        tags = ", ".join(client.tags) if client.tags else "None"

        return (
            f"👤 {client.name} (ID: {client.id})\n"
            f"Age: {client.age} | {client.occupation} | {client.city}\n"
            f"Risk Profile: {client.risk_profile}\n"
            f"Investment Horizon: {client.investment_horizon} years\n"
            f"Total Wealth: ₹{client.total_investable_wealth} Cr\n"
            f"AUM with Us: ₹{client.current_aum_with_us} Cr\n"
            f"Annual Income: ₹{client.annual_income} Cr\n\n"
            f"📊 Current Holdings:\n{holdings_text}\n\n"
            f"🎯 Goals:\n{goals_text}\n\n"
            f"👨‍👩‍👧 Family:\n{family_text}\n\n"
            f"📅 Last Review: {client.last_review_date}\n"
            f"📅 Next Review: {client.next_review_date}\n"
            f"📅 First Investment: {client.first_investment_date}\n"
            f"Tags: {tags}\n"
            f"Prefers: {client.communication_preference}\n"
            f"Notes: {client.notes or 'None'}"
        )
    finally:
        session.close()
