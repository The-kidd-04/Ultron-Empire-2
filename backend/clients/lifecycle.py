"""
Ultron Empire — Client Lifecycle Management
Tracks client journey stages and life events.
"""

import logging
from datetime import date, timedelta
from backend.db.database import SessionLocal
from backend.db.models import Client

logger = logging.getLogger(__name__)

LIFECYCLE_STAGES = {
    "prospect": "Not yet invested",
    "new": "Invested < 6 months ago",
    "active": "Invested > 6 months, regular reviews",
    "mature": "Invested > 2 years",
    "dormant": "No review in 6+ months",
    "at_risk": "Portfolio underperforming or complaints",
}


def classify_client_stage(client: Client) -> str:
    """Classify client into lifecycle stage."""
    today = date.today()

    if not client.first_investment_date:
        return "prospect"

    months_since_first = (today - client.first_investment_date).days / 30

    if months_since_first < 6:
        return "new"

    if client.last_review_date:
        months_since_review = (today - client.last_review_date).days / 30
        if months_since_review > 6:
            return "dormant"

    if months_since_first > 24:
        return "mature"

    return "active"


def get_lifecycle_summary() -> dict:
    """Get summary of clients by lifecycle stage."""
    session = SessionLocal()
    try:
        clients = session.query(Client).all()
        summary = {stage: [] for stage in LIFECYCLE_STAGES}

        for c in clients:
            stage = classify_client_stage(c)
            summary[stage].append({
                "id": c.id,
                "name": c.name,
                "aum": c.current_aum_with_us,
            })

        return {
            stage: {"count": len(clients_list), "clients": clients_list}
            for stage, clients_list in summary.items()
        }
    finally:
        session.close()
