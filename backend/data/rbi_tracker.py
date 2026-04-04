"""
Ultron Empire — RBI Policy Tracking (Feature 2.3)
Monitors RBI monetary policy announcements and rate decisions.
"""

import logging
import httpx
from backend.config import settings

logger = logging.getLogger(__name__)

RBI_CURRENT = {
    "repo_rate": 6.25,
    "reverse_repo": 3.35,
    "crr": 4.0,
    "slr": 18.0,
    "last_action": "cut",
    "last_action_date": "2025-02-07",
    "next_meeting": "2026-04-09",
    "cpi_inflation": 4.2,
    "stance": "accommodative",
}

RATE_HISTORY = [
    {"date": "2025-02-07", "action": "cut", "change": -0.25, "repo": 6.25},
    {"date": "2024-10-09", "action": "pause", "change": 0, "repo": 6.50},
    {"date": "2023-02-08", "action": "hike", "change": 0.25, "repo": 6.50},
]


async def fetch_rbi_updates() -> list:
    """Fetch latest RBI news and policy updates."""
    if not settings.TAVILY_API_KEY:
        return []
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        results = client.search(
            query="RBI monetary policy rate decision India 2026",
            search_depth="advanced", max_results=5,
            include_domains=["rbi.org.in", "economictimes.com", "livemint.com"],
        )
        return [{"title": r["title"], "url": r["url"], "summary": r["content"][:300]} for r in results.get("results", [])]
    except Exception as e:
        logger.error(f"RBI tracker failed: {e}")
        return []


def get_rbi_impact_analysis() -> dict:
    """Analyze current RBI stance and impact on fund categories."""
    from backend.prediction.rate_cycle import analyze_rate_cycle
    return analyze_rate_cycle(
        current_repo_rate=RBI_CURRENT["repo_rate"],
        last_action=RBI_CURRENT["last_action"],
        inflation_cpi=RBI_CURRENT["cpi_inflation"],
    )
