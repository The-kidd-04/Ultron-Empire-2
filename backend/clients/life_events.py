"""
Ultron Empire — Life Event Detection (Feature 4.6)
Monitors news/social for client life events signaling new investable wealth.
"""

import logging
from backend.config import settings

logger = logging.getLogger(__name__)


async def scan_client_life_events(client_name: str) -> list:
    """Search for life events for a specific client."""
    if not settings.TAVILY_API_KEY:
        return [{"note": "Life event detection requires Tavily API key"}]
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        results = client.search(
            query=f"{client_name} India promotion CEO funding IPO business exit property",
            search_depth="basic", max_results=3,
        )
        events = []
        for r in results.get("results", []):
            events.append({
                "title": r["title"],
                "url": r["url"],
                "summary": r["content"][:200],
                "signal": "Potential new investable wealth detected",
            })
        return events
    except Exception as e:
        logger.error(f"Life event scan failed: {e}")
        return []


def check_family_milestones() -> list:
    """Check for family-related milestones (children turning 18/25, etc.)."""
    from datetime import date
    from backend.db.database import SessionLocal
    from backend.db.models import Client

    session = SessionLocal()
    try:
        clients = session.query(Client).all()
        milestones = []
        today = date.today()

        for c in clients:
            for fm in (c.family_members or []):
                age = fm.get("age", 0)
                name = fm.get("name", "")
                relation = fm.get("relation", "")

                if age == 17:
                    milestones.append({
                        "client": c.name, "family_member": name, "relation": relation,
                        "milestone": f"{name} turns 18 next year — discuss starting investment journey",
                    })
                elif age == 24:
                    milestones.append({
                        "client": c.name, "family_member": name, "relation": relation,
                        "milestone": f"{name} turns 25 next year — potential new client for PMS",
                    })
                elif relation.lower() == "son" and age >= 28:
                    milestones.append({
                        "client": c.name, "family_member": name, "relation": relation,
                        "milestone": f"{name} (age {age}) — discuss inter-generational wealth transfer planning",
                    })
        return milestones
    finally:
        session.close()
