"""
Ultron Empire — KYC & Certification Tracker
Tracks client KYC expiry and distributor certification renewals.
"""

import logging
from datetime import date, timedelta
from backend.db.database import SessionLocal
from backend.db.models import Client

logger = logging.getLogger(__name__)


def get_expiring_kyc(days_ahead: int = 60) -> list:
    """Get clients whose KYC documents may need renewal."""
    # KYC is typically valid for 10 years, but periodic updates needed
    # This tracks clients who haven't updated in 2+ years
    session = SessionLocal()
    try:
        cutoff = date.today() - timedelta(days=730)  # 2 years
        clients = session.query(Client).filter(
            Client.first_investment_date <= cutoff
        ).all()

        results = []
        for c in clients:
            years_since = (date.today() - c.first_investment_date).days / 365
            if years_since >= 2:
                results.append({
                    "id": c.id,
                    "name": c.name,
                    "first_investment": str(c.first_investment_date),
                    "years_since_kyc": round(years_since, 1),
                    "priority": "high" if years_since >= 5 else "medium",
                })
        return results
    finally:
        session.close()


# AMFI/NISM certification tracking for Ishaan
CERTIFICATIONS = {
    "NISM Series V-A": {
        "description": "Mutual Fund Distributors Certification",
        "validity_years": 3,
        "renewal_exam": True,
    },
    "NISM Series X-A": {
        "description": "Investment Adviser (Level 1)",
        "validity_years": 3,
        "renewal_exam": True,
    },
    "NISM Series X-B": {
        "description": "Investment Adviser (Level 2)",
        "validity_years": 3,
        "renewal_exam": True,
    },
}


def check_certification_renewals(cert_expiry_dates: dict) -> list:
    """Check which certifications need renewal.

    Args:
        cert_expiry_dates: {"NISM Series V-A": "2026-08-15", ...}
    """
    alerts = []
    today = date.today()
    for cert, expiry_str in cert_expiry_dates.items():
        try:
            expiry = date.fromisoformat(expiry_str)
            days_until = (expiry - today).days
            if days_until <= 90:
                alerts.append({
                    "certification": cert,
                    "expiry_date": expiry_str,
                    "days_until_expiry": days_until,
                    "urgency": "critical" if days_until <= 30 else "important",
                    "action": f"Schedule {CERTIFICATIONS.get(cert, {}).get('description', cert)} renewal exam",
                })
        except ValueError:
            continue
    return alerts
