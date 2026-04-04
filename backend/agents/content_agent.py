"""
Ultron Empire — Content Generation Agent
Generates market briefs, social posts, newsletters, client messages.
"""

import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from backend.config import settings
from backend.utils.brand import BRAND_NAME, TAGLINE, WEBSITE, TELEGRAM_FOOTER

logger = logging.getLogger(__name__)

llm = ChatAnthropic(
    model=settings.CLAUDE_MODEL,
    api_key=settings.ANTHROPIC_API_KEY,
    temperature=0.5,
    max_tokens=2048,
)

CONTENT_SYSTEM = f"""You are Ultron's content creation engine for {BRAND_NAME} — {TAGLINE}.

Brand voice:
- Authoritative yet approachable — trusted advisor, not salesperson
- AI-forward — emphasize technology without being cold
- Premium — targeting HNIs, NRIs, Family Offices
- Indian market native — use ₹, Cr, L, Nifty, Sensex naturally
- Always back statements with data, never generic advice

Website: {WEBSITE}
"""


async def generate_morning_brief(market_data: dict, news: list, fii_dii: dict) -> str:
    """Generate the daily morning brief."""
    context = (
        f"Market data: {market_data}\n"
        f"Top news: {news}\n"
        f"FII/DII flows: {fii_dii}"
    )
    response = await llm.ainvoke([
        SystemMessage(content=CONTENT_SYSTEM + "\nGenerate a morning market brief for Telegram. Use the morning brief template format with emojis, sections for Global Cues, India Pre-Market, Flows, Key Events, and Ultron's Take."),
        HumanMessage(content=context),
    ])
    return response.content


async def generate_social_post(topic: str, data: dict = None) -> str:
    """Generate an Instagram/LinkedIn post."""
    response = await llm.ainvoke([
        SystemMessage(content=CONTENT_SYSTEM + "\nGenerate a social media post (Instagram/LinkedIn). Include data points, insights, relevant hashtags. Keep it engaging and professional."),
        HumanMessage(content=f"Topic: {topic}\nData: {data or 'Use your knowledge'}"),
    ])
    return response.content


async def generate_client_message(
    client_name: str,
    context: str,
    tone: str = "professional",
) -> str:
    """Draft a client communication message."""
    response = await llm.ainvoke([
        SystemMessage(content=CONTENT_SYSTEM + f"\nDraft a {tone} WhatsApp/email message to a client. Be reassuring if discussing losses, celebratory for gains. Always include a call to action."),
        HumanMessage(content=f"Client: {client_name}\nContext: {context}"),
    ])
    return response.content


async def generate_newsletter(market_recap: str, fund_highlights: str, outlook: str) -> str:
    """Generate monthly newsletter content."""
    response = await llm.ainvoke([
        SystemMessage(content=CONTENT_SYSTEM + "\nGenerate a monthly newsletter for HNI clients. Sections: Market Recap, Fund Highlights, Ultron's Outlook, Tax Tips. Professional, data-rich, actionable."),
        HumanMessage(content=f"Market Recap: {market_recap}\nFund Highlights: {fund_highlights}\nOutlook: {outlook}"),
    ])
    return response.content
