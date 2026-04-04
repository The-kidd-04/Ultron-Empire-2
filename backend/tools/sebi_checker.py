"""
Ultron Empire — SEBI Circular Checker Tool
Searches for recent SEBI circulars and regulatory updates.
"""

from langchain_core.tools import tool
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


@tool
def sebi_checker_tool(query: str = "PMS AIF regulation") -> str:
    """Search for recent SEBI circulars and regulatory updates.

    Args:
        query: Search term (e.g., "PMS fee structure", "AIF regulation", "distributor compliance")

    Returns:
        Recent SEBI circulars and regulatory news relevant to the query.
    """
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = client.search(
            query=f"SEBI {query} circular regulation 2025 2026",
            search_depth="advanced",
            max_results=5,
            include_domains=[
                "sebi.gov.in", "economictimes.com", "moneycontrol.com",
                "livemint.com", "taxguru.in", "caclubindia.com",
            ],
        )

        results = response.get("results", [])
        if not results:
            return f"No recent SEBI circulars found for '{query}'."

        output = []
        for r in results:
            content = r.get("content", "")[:400]
            output.append(
                f"📋 {r.get('title', 'No title')}\n"
                f"Source: {r.get('url', 'N/A')}\n"
                f"{content}..."
            )

        return "\n\n---\n\n".join(output)

    except Exception as e:
        logger.error(f"SEBI checker failed: {e}")
        return f"SEBI circular search temporarily unavailable. Error: {str(e)}"
