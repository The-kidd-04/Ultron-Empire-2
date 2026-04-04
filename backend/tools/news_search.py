"""
Ultron Empire — News Search Tool
Searches for recent financial news using Tavily (AI-optimized search).
"""

from langchain_core.tools import tool
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


@tool
def news_search_tool(query: str, max_results: int = 5) -> str:
    """Search for recent financial news relevant to Indian markets.

    Args:
        query: Search term (e.g., "SEBI PMS regulation", "Quant PMS performance")
        max_results: Number of results to return (default 5)

    Returns:
        Recent news articles with title, source, date, and summary.
    """
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = client.search(
            query=f"{query} India finance market",
            search_depth="advanced",
            max_results=max_results,
            include_domains=[
                "economictimes.com", "moneycontrol.com", "livemint.com",
                "reuters.com", "bloomberg.com", "sebi.gov.in",
                "bseindia.com", "nseindia.com", "valueresearchonline.com",
                "morningstar.in",
            ],
        )

        results = response.get("results", [])
        if not results:
            return f"No recent news found for '{query}'."

        output = []
        for r in results:
            content = r.get("content", "")[:300]
            output.append(
                f"📰 {r.get('title', 'No title')}\n"
                f"Source: {r.get('url', 'N/A')}\n"
                f"{content}..."
            )

        return "\n\n---\n\n".join(output)

    except Exception as e:
        logger.error(f"News search failed: {e}")
        return f"News search temporarily unavailable. Error: {str(e)}"
