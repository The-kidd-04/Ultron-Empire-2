"""
Ultron Empire — SEBI Monitor Pipeline
Scrapes SEBI website for new circulars affecting PMS/AIF/MF.
"""

import logging
from datetime import datetime
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SEBI_CIRCULARS_URL = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=0&smid=0"


async def fetch_latest_circulars(max_results: int = 10) -> list:
    """Fetch latest SEBI circulars from the website."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(SEBI_CIRCULARS_URL, timeout=20)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        circulars = []

        # Parse circular listings (structure may change)
        rows = soup.select("table tr") or soup.select(".list-item")
        for row in rows[:max_results]:
            try:
                links = row.find_all("a")
                if links:
                    title = links[0].get_text(strip=True)
                    url = links[0].get("href", "")
                    if not url.startswith("http"):
                        url = f"https://www.sebi.gov.in{url}"
                    date_text = row.find("td") or row.find("span")
                    circulars.append({
                        "title": title,
                        "url": url,
                        "date": date_text.get_text(strip=True) if date_text else "",
                    })
            except Exception:
                continue

        return circulars
    except Exception as e:
        logger.error(f"SEBI circular fetch failed: {e}")
        return []


def filter_relevant_circulars(circulars: list) -> list:
    """Filter circulars relevant to PMS/AIF/MF business."""
    keywords = [
        "portfolio management", "pms", "alternative investment", "aif",
        "mutual fund", "distributor", "investment adviser", "sebi registration",
        "fee structure", "disclosure", "compliance", "investor protection",
    ]
    relevant = []
    for c in circulars:
        title_lower = c["title"].lower()
        if any(kw in title_lower for kw in keywords):
            c["relevance"] = "high"
            relevant.append(c)
    return relevant
