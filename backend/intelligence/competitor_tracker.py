"""
Ultron Empire — Competitor Intelligence Tracker
Monitors competitor PMS/AIF distributors and fund houses.
"""

import logging
from backend.config import settings

logger = logging.getLogger(__name__)

COMPETITORS = [
    {"name": "PMS Bazaar", "website": "pmsbazaar.com", "type": "aggregator"},
    {"name": "PMS AIF World", "website": "pmsaifworld.com", "type": "aggregator"},
    {"name": "Wealthy.in", "website": "wealthy.in", "type": "distributor"},
    {"name": "Investwell", "website": "investwell.in", "type": "platform"},
    {"name": "WealthDesk", "website": "wealthdesk.in", "type": "platform"},
]


async def scan_competitor_updates() -> list:
    """Scan competitor websites for new launches, updates."""
    if not settings.TAVILY_API_KEY:
        return [{"note": "Competitor scanning requires Tavily API key"}]

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)

        updates = []
        for competitor in COMPETITORS:
            try:
                results = client.search(
                    query=f"{competitor['name']} PMS AIF new launch update",
                    search_depth="basic",
                    max_results=2,
                    include_domains=[competitor["website"]],
                )
                for r in results.get("results", []):
                    updates.append({
                        "competitor": competitor["name"],
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "summary": r.get("content", "")[:200],
                    })
            except Exception:
                continue

        return updates

    except Exception as e:
        logger.error(f"Competitor scan failed: {e}")
        return []
