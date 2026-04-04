"""
Ultron Empire — Anniversary & Milestone Tracking (Feature 4.8)
Tracks investment anniversaries, goal progress, and portfolio milestones.
"""

import logging
from datetime import date, timedelta
from backend.db.database import SessionLocal
from backend.db.models import Client

logger = logging.getLogger(__name__)


def get_upcoming_anniversaries(days_ahead: int = 30) -> list:
    """Find investment anniversaries coming up."""
    session = SessionLocal()
    try:
        clients = session.query(Client).filter(Client.first_investment_date.isnot(None)).all()
        today = date.today()
        anniversaries = []

        for c in clients:
            anni_this_year = c.first_investment_date.replace(year=today.year)
            if today <= anni_this_year <= today + timedelta(days=days_ahead):
                years = today.year - c.first_investment_date.year
                anniversaries.append({
                    "client": c.name,
                    "anniversary_date": str(anni_this_year),
                    "years_with_us": years,
                    "aum": c.current_aum_with_us,
                    "message": f"🎉 {years} year anniversary! AUM: ₹{c.current_aum_with_us} Cr",
                    "suggested_action": f"/celebrate {c.name}",
                })
        return anniversaries
    finally:
        session.close()


def check_goal_milestones() -> list:
    """Check clients who've reached goal milestones (30%, 50%, 75%, 100%)."""
    session = SessionLocal()
    try:
        clients = session.query(Client).all()
        milestones = []

        for c in clients:
            aum = c.current_aum_with_us or 0
            for g in (c.goals or []):
                target = g.get("target", 0)
                if target <= 0:
                    continue
                progress = (aum / target) * 100

                for threshold in [30, 50, 75, 100]:
                    if progress >= threshold and progress < threshold + 10:
                        milestones.append({
                            "client": c.name,
                            "goal": g.get("name", "Unknown"),
                            "target_cr": target,
                            "current_cr": aum,
                            "progress_pct": round(progress, 1),
                            "milestone": f"{threshold}% of {g['name']} goal reached!",
                        })
                        break
        return milestones
    finally:
        session.close()


def get_portfolio_milestones() -> list:
    """Detect portfolio milestones (crossing ₹1Cr, ₹5Cr, etc.)."""
    session = SessionLocal()
    try:
        clients = session.query(Client).all()
        milestones_cr = [0.5, 1, 2, 3, 5, 10, 25, 50]
        results = []

        for c in clients:
            aum = c.current_aum_with_us or 0
            for m in milestones_cr:
                if aum >= m and aum < m * 1.1:  # Just crossed this milestone
                    results.append({
                        "client": c.name,
                        "aum": aum,
                        "milestone": f"Portfolio crossed ₹{m} Cr!",
                    })
                    break
        return results
    finally:
        session.close()
