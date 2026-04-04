"""
Ultron Empire — IPO and NFO Tracking (Feature 2.7)
Tracks new IPOs, NFOs, and PMS strategy launches.
"""

import logging
from backend.config import settings

logger = logging.getLogger(__name__)


async def scan_upcoming_ipos() -> list:
    """Scan for upcoming and recent IPOs."""
    if not settings.TAVILY_API_KEY:
        return []
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        results = client.search(
            query="upcoming IPO India 2026 listing date GMP",
            search_depth="advanced", max_results=5,
            include_domains=["chittorgarh.com", "moneycontrol.com", "ipowatch.in"],
        )
        return [{"title": r["title"], "url": r["url"], "summary": r["content"][:300]} for r in results.get("results", [])]
    except Exception as e:
        logger.error(f"IPO tracker failed: {e}")
        return []


async def scan_new_nfos() -> list:
    """Scan for new NFOs (New Fund Offers) from AMCs."""
    if not settings.TAVILY_API_KEY:
        return []
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        results = client.search(
            query="new NFO mutual fund India 2026 launch",
            search_depth="basic", max_results=5,
            include_domains=["valueresearchonline.com", "moneycontrol.com", "morningstar.in"],
        )
        return [{"title": r["title"], "url": r["url"], "summary": r["content"][:300]} for r in results.get("results", [])]
    except Exception as e:
        logger.error(f"NFO tracker failed: {e}")
        return []


def analyze_ipo_for_clients(ipo_name: str, sector: str, valuation_pe: float) -> dict:
    """Quick analysis of an IPO's relevance to PMS portfolios."""
    from backend.db.database import SessionLocal
    from backend.db.models import FundData

    session = SessionLocal()
    try:
        # Find funds in the same sector
        related = session.query(FundData).all()
        affected = []
        for f in related:
            alloc = f.sector_allocation or {}
            if sector in alloc and alloc[sector] > 10:
                affected.append({"fund": f.fund_name, "sector_weight": alloc[sector]})

        return {
            "ipo": ipo_name,
            "sector": sector,
            "valuation_pe": valuation_pe,
            "funds_in_same_sector": affected,
            "note": "New IPOs may become PMS holdings if they meet fund manager criteria",
        }
    finally:
        session.close()
