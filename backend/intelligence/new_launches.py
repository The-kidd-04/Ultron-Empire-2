"""
Ultron Empire — New Fund Launch Analyzer
Tracks and analyzes new PMS/AIF strategy launches.
"""

import logging
from backend.config import settings

logger = logging.getLogger(__name__)


async def scan_new_launches() -> list:
    """Scan for newly launched PMS/AIF strategies."""
    if not settings.TAVILY_API_KEY:
        return []

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)

        results = client.search(
            query="new PMS launch India 2026 portfolio management service",
            search_depth="advanced",
            max_results=5,
        )

        launches = []
        for r in results.get("results", []):
            launches.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "summary": r.get("content", "")[:300],
            })
        return launches

    except Exception as e:
        logger.error(f"New launch scan failed: {e}")
        return []


def analyze_new_fund(
    fund_name: str,
    fund_house: str,
    strategy: str,
    min_investment: float,
    fee_structure: dict,
) -> dict:
    """Quick analysis of a newly launched fund.

    Returns competitive positioning and recommendation.
    """
    # Compare against existing universe
    from backend.db.database import SessionLocal
    from backend.db.models import FundData

    session = SessionLocal()
    try:
        similar = session.query(FundData).filter(
            FundData.strategy == strategy
        ).order_by(FundData.returns_1y.desc()).limit(5).all()

        avg_return = sum(f.returns_1y or 0 for f in similar) / max(len(similar), 1)
        avg_fee_fixed = sum(
            (f.fee_structure or {}).get("fixed", 0) for f in similar
        ) / max(len(similar), 1)

        return {
            "fund": fund_name,
            "house": fund_house,
            "strategy": strategy,
            "competitive_landscape": {
                "similar_funds": len(similar),
                "avg_peer_return_1y": round(avg_return, 1),
                "avg_peer_fixed_fee": round(avg_fee_fixed, 1),
                "top_peer": similar[0].fund_name if similar else "N/A",
            },
            "fee_analysis": {
                "fixed": fee_structure.get("fixed", 0),
                "performance": fee_structure.get("performance", 0),
                "vs_avg": "Higher" if fee_structure.get("fixed", 0) > avg_fee_fixed else "Lower",
            },
            "recommendation": "Track for 6 months before recommending to clients — no track record yet.",
        }
    finally:
        session.close()
