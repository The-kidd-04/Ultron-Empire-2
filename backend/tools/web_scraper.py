"""
Ultron Empire — Web Scraper Tool
Firecrawl-based clean web scraping for financial data.
"""

from langchain_core.tools import tool
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


@tool
def web_scraper_tool(url: str, extract_type: str = "text") -> str:
    """Scrape a web page and extract clean content.

    Args:
        url: URL to scrape
        extract_type: What to extract — "text" (full page text), "tables" (structured data), "links" (all links)

    Returns:
        Extracted content from the webpage.
    """
    if not settings.FIRECRAWL_API_KEY:
        # Fallback to basic httpx scraping
        try:
            import httpx
            from bs4 import BeautifulSoup

            response = httpx.get(url, timeout=15, follow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()

            if extract_type == "text":
                text = soup.get_text(separator="\n", strip=True)
                return text[:3000]  # Limit output

            elif extract_type == "tables":
                tables = soup.find_all("table")
                if not tables:
                    return "No tables found on this page."
                result = []
                for i, table in enumerate(tables[:3]):
                    rows = table.find_all("tr")
                    table_text = []
                    for row in rows[:20]:
                        cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
                        table_text.append(" | ".join(cells))
                    result.append(f"Table {i+1}:\n" + "\n".join(table_text))
                return "\n\n".join(result)

            elif extract_type == "links":
                links = soup.find_all("a", href=True)
                return "\n".join(
                    f"{a.get_text(strip=True)}: {a['href']}"
                    for a in links[:30] if a.get_text(strip=True)
                )

            else:
                return f"Unknown extract_type: {extract_type}"

        except Exception as e:
            logger.error(f"Web scraping failed: {e}")
            return f"Scraping failed: {str(e)}"

    # Use Firecrawl if API key available
    try:
        from firecrawl import FirecrawlApp

        app = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY)
        result = app.scrape_url(url, params={"formats": ["markdown"]})

        content = result.get("markdown", result.get("content", "No content extracted"))
        return content[:3000]

    except Exception as e:
        logger.error(f"Firecrawl scraping failed: {e}")
        return f"Scraping failed: {str(e)}"
