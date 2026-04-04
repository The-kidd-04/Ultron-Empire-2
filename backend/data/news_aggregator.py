"""
Ultron Empire — News Aggregator Pipeline
Multi-source news aggregation: NewsAPI + Google RSS + Tavily.
"""

import logging
from typing import Optional
import httpx
import feedparser

from backend.config import settings

logger = logging.getLogger(__name__)

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

FINANCIAL_SOURCES = [
    "economictimes.com", "moneycontrol.com", "livemint.com",
    "reuters.com", "bloomberg.com", "sebi.gov.in",
    "bseindia.com", "nseindia.com", "valueresearchonline.com",
]


async def search_newsapi(query: str, max_results: int = 5) -> list:
    """Search NewsAPI for financial news."""
    if not settings.NEWS_API_KEY:
        return []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": max_results,
                    "apiKey": settings.NEWS_API_KEY,
                    "domains": ",".join(FINANCIAL_SOURCES[:5]),
                },
                timeout=15,
            )
            data = response.json()
            return [
                {
                    "title": a["title"],
                    "source": a["source"]["name"],
                    "url": a["url"],
                    "summary": a.get("description", ""),
                    "published": a.get("publishedAt", ""),
                }
                for a in data.get("articles", [])
            ]
    except Exception as e:
        logger.error(f"NewsAPI search failed: {e}")
        return []


def search_google_rss(query: str, max_results: int = 5) -> list:
    """Search Google News RSS feed."""
    try:
        url = GOOGLE_NEWS_RSS.format(query=query.replace(" ", "+"))
        feed = feedparser.parse(url)
        return [
            {
                "title": entry.title,
                "source": "Google News",
                "url": entry.link,
                "summary": entry.get("summary", ""),
                "published": entry.get("published", ""),
            }
            for entry in feed.entries[:max_results]
        ]
    except Exception as e:
        logger.error(f"Google RSS search failed: {e}")
        return []


async def aggregate_news(query: str = "India PMS AIF market", max_results: int = 10) -> list:
    """Aggregate news from multiple sources, deduplicate."""
    all_news = []

    # NewsAPI
    newsapi_results = await search_newsapi(query, max_results=max_results // 2)
    all_news.extend(newsapi_results)

    # Google RSS
    rss_results = search_google_rss(query, max_results=max_results // 2)
    all_news.extend(rss_results)

    # Deduplicate by title similarity
    seen_titles = set()
    unique = []
    for item in all_news:
        title_key = item["title"][:50].lower()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique.append(item)

    return unique[:max_results]
