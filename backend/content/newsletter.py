"""Ultron Empire — Monthly Newsletter Generator"""

from backend.agents.content_agent import generate_newsletter


async def generate_monthly_newsletter(market_recap: str = "", fund_highlights: str = "", outlook: str = "") -> str:
    return await generate_newsletter(market_recap=market_recap, fund_highlights=fund_highlights, outlook=outlook)
