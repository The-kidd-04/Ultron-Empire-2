"""
Ultron Empire — Dashboard API (V3 Jarvis)
GET /dashboard — Aggregated data for the home dashboard.
"""

from fastapi import APIRouter
from backend.db.database import SessionLocal
from backend.db.models import Client, Alert, FundData
from backend.utils.date_utils import today_ist

router = APIRouter()


@router.get("")
async def get_dashboard():
    """Get aggregated dashboard data in one call."""
    session = SessionLocal()
    try:
        # Client stats
        clients = session.query(Client).all()
        total_aum = sum(c.current_aum_with_us or 0 for c in clients)

        # Recent alerts
        alerts = session.query(Alert).order_by(Alert.created_at.desc()).limit(5).all()
        alert_data = [
            {"id": a.id, "priority": a.priority, "title": a.title, "created_at": a.created_at.isoformat() if a.created_at else None}
            for a in alerts
        ]

        # Pending reviews
        today = today_ist()
        overdue = [c for c in clients if c.next_review_date and c.next_review_date <= today]

        # Critical alert count
        critical_count = session.query(Alert).filter(Alert.priority == "critical", Alert.is_read == False).count()
        important_count = session.query(Alert).filter(Alert.priority == "important", Alert.is_read == False).count()

        return {
            "market": {"note": "Call /api/v1/market for live data"},
            "aum": {
                "total_cr": round(total_aum, 2),
                "client_count": len(clients),
            },
            "alerts": {
                "critical": critical_count,
                "important": important_count,
                "recent": alert_data,
            },
            "reviews": {
                "overdue_count": len(overdue),
                "overdue_clients": [{"name": c.name, "due": str(c.next_review_date)} for c in overdue[:5]],
            },
            "fund_universe": session.query(FundData).count(),
        }
    finally:
        session.close()
