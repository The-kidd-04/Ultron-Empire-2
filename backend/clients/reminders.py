"""
Ultron Empire — Client Reminders
Review dates, renewals, anniversaries, life events.
"""

import logging
from datetime import date, timedelta
from backend.db.database import SessionLocal
from backend.db.models import Client

logger = logging.getLogger(__name__)


def get_upcoming_reviews(days_ahead: int = 14) -> list:
    """Get clients with upcoming review dates."""
    session = SessionLocal()
    try:
        today = date.today()
        cutoff = today + timedelta(days=days_ahead)
        clients = session.query(Client).filter(
            Client.next_review_date.between(today, cutoff)
        ).order_by(Client.next_review_date).all()

        return [
            {
                "id": c.id,
                "name": c.name,
                "next_review": str(c.next_review_date),
                "days_until": (c.next_review_date - today).days,
                "aum": c.current_aum_with_us,
                "risk_profile": c.risk_profile,
            }
            for c in clients
        ]
    finally:
        session.close()


def get_investment_anniversaries(days_ahead: int = 30) -> list:
    """Find clients with investment anniversaries coming up."""
    session = SessionLocal()
    try:
        today = date.today()
        clients = session.query(Client).filter(Client.first_investment_date.isnot(None)).all()

        anniversaries = []
        for c in clients:
            if c.first_investment_date:
                anni_this_year = c.first_investment_date.replace(year=today.year)
                if today <= anni_this_year <= today + timedelta(days=days_ahead):
                    years = today.year - c.first_investment_date.year
                    anniversaries.append({
                        "id": c.id,
                        "name": c.name,
                        "anniversary_date": str(anni_this_year),
                        "years_with_us": years,
                        "aum": c.current_aum_with_us,
                    })
        return anniversaries
    finally:
        session.close()


def get_overdue_reviews() -> list:
    """Get clients whose review date has passed."""
    session = SessionLocal()
    try:
        today = date.today()
        clients = session.query(Client).filter(
            Client.next_review_date < today
        ).order_by(Client.next_review_date).all()

        return [
            {
                "id": c.id,
                "name": c.name,
                "review_was_due": str(c.next_review_date),
                "days_overdue": (today - c.next_review_date).days,
                "aum": c.current_aum_with_us,
            }
            for c in clients
        ]
    finally:
        session.close()
