"""
Ultron Empire — Lead Intelligence (Feature 8.4)
LinkedIn research, event attendee scoring, referral mapping, pre-call research.
"""

import logging
from backend.config import settings
from backend.clients.scoring import calculate_lead_score

logger = logging.getLogger(__name__)


async def research_prospect(name: str) -> dict:
    """Auto-research a prospect before a cold call."""
    if not settings.TAVILY_API_KEY:
        return {"error": "Requires Tavily API key for research"}
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        results = client.search(
            query=f"{name} India CEO director founder business company net worth LinkedIn",
            search_depth="advanced", max_results=5,
        )

        profile = {"name": name, "findings": [], "estimated_profile": {}}
        for r in results.get("results", []):
            content = r["content"].lower()
            profile["findings"].append({"title": r["title"], "url": r["url"], "summary": r["content"][:200]})

            # Estimate profile from search results
            if any(w in content for w in ["ceo", "founder", "director", "managing"]):
                profile["estimated_profile"]["role"] = "Senior Executive / Founder"
            if any(w in content for w in ["crore", "million", "funding", "ipo"]):
                profile["estimated_profile"]["wealth_indicator"] = "High"

        # Score the lead
        profile["lead_score"] = calculate_lead_score(
            total_wealth_cr=5,  # Estimated
            age=45,  # Default
            occupation=profile["estimated_profile"].get("role", "Professional"),
            city="Mumbai",  # Default
            risk_profile="Moderate",
            referral=False,
        )

        return profile
    except Exception as e:
        logger.error(f"Prospect research failed: {e}")
        return {"error": str(e)}


def score_event_attendees(attendees: list) -> list:
    """Score and rank event attendees by investment potential.

    Args:
        attendees: [{"name": "...", "company": "...", "designation": "..."}]
    """
    scored = []
    for a in attendees:
        designation = a.get("designation", "").lower()

        # Estimate wealth based on designation
        if any(w in designation for w in ["ceo", "founder", "chairman", "promoter"]):
            est_wealth = 25
        elif any(w in designation for w in ["cfo", "coo", "director", "vp", "partner"]):
            est_wealth = 10
        elif any(w in designation for w in ["doctor", "lawyer", "ca", "consultant"]):
            est_wealth = 5
        else:
            est_wealth = 2

        score = calculate_lead_score(
            total_wealth_cr=est_wealth, age=45,
            occupation=a.get("designation", "Professional"),
            city=a.get("city", "Mumbai"),
            risk_profile="Moderate", referral=False,
        )

        scored.append({
            **a,
            "estimated_wealth_cr": est_wealth,
            "score": score["score"],
            "tier": score["tier"],
            "action": score["recommended_action"],
        })

    return sorted(scored, key=lambda x: -x["score"])


def find_referral_opportunities(client_name: str) -> dict:
    """Find referral opportunities from existing client's network."""
    from backend.db.database import SessionLocal
    from backend.db.models import Client

    session = SessionLocal()
    try:
        client = session.query(Client).filter(Client.name.ilike(f"%{client_name}%")).first()
        if not client:
            return {"error": "Client not found"}

        family = client.family_members or []
        referral_opportunities = []
        for fm in family:
            age = fm.get("age", 0)
            if age >= 25:
                referral_opportunities.append({
                    "name": fm["name"],
                    "relation": fm["relation"],
                    "age": age,
                    "potential": "Direct investment prospect" if age >= 30 else "SIP/MF prospect",
                })

        return {
            "client": client.name,
            "family_referrals": referral_opportunities,
            "note": f"{len(referral_opportunities)} potential referrals from {client.name}'s family",
        }
    finally:
        session.close()
