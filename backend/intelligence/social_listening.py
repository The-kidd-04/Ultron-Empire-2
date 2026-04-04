"""
Ultron Empire — Social Listening & Sentiment (Feature 8.3)
Tracks big investor moves, Twitter sentiment, finfluencer monitoring.
"""

import logging
from backend.config import settings

logger = logging.getLogger(__name__)

BIG_INVESTORS = [
    "Ashish Kacholia", "Dolly Khanna", "Vijay Kedia",
    "Rakesh Jhunjhunwala (estate)", "Sunil Singhania", "Porinju Veliyath",
    "Basant Maheshwari", "Kenneth Andrade",
]


async def track_big_investor_moves() -> list:
    """Track portfolio changes of well-known investors."""
    if not settings.TAVILY_API_KEY:
        return []
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        updates = []
        for investor in BIG_INVESTORS[:4]:  # Limit API calls
            results = client.search(
                query=f"{investor} portfolio buy sell stake increase decrease 2026",
                search_depth="basic", max_results=2,
            )
            for r in results.get("results", []):
                updates.append({
                    "investor": investor,
                    "title": r["title"],
                    "url": r["url"],
                    "summary": r["content"][:200],
                })
        return updates
    except Exception as e:
        logger.error(f"Big investor tracking failed: {e}")
        return []


async def scan_stock_sentiment(stock_name: str) -> dict:
    """Scan social media sentiment for a specific stock."""
    if not settings.TAVILY_API_KEY:
        return {"error": "Requires Tavily API key"}
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        results = client.search(
            query=f"{stock_name} stock sentiment Twitter Reddit opinion analysis India",
            search_depth="advanced", max_results=5,
        )

        positive = negative = neutral = 0
        mentions = []
        for r in results.get("results", []):
            content = r["content"].lower()
            if any(w in content for w in ["bullish", "buy", "positive", "strong", "upgrade"]):
                positive += 1
            elif any(w in content for w in ["bearish", "sell", "negative", "weak", "downgrade"]):
                negative += 1
            else:
                neutral += 1
            mentions.append({"title": r["title"], "url": r["url"]})

        total = positive + negative + neutral
        return {
            "stock": stock_name,
            "sentiment": "Positive" if positive > negative else "Negative" if negative > positive else "Neutral",
            "positive": positive, "negative": negative, "neutral": neutral,
            "confidence": f"{max(positive, negative) / max(total, 1) * 100:.0f}%",
            "recent_mentions": mentions[:5],
        }
    except Exception as e:
        logger.error(f"Sentiment scan failed: {e}")
        return {"error": str(e)}


async def monitor_finfluencers() -> list:
    """Monitor what financial influencers are promoting."""
    if not settings.TAVILY_API_KEY:
        return []
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        results = client.search(
            query="best PMS India 2026 recommendation YouTube finfluencer",
            search_depth="basic", max_results=5,
        )
        return [{"title": r["title"], "url": r["url"], "summary": r["content"][:200]} for r in results.get("results", [])]
    except Exception as e:
        logger.error(f"Finfluencer monitoring failed: {e}")
        return []
