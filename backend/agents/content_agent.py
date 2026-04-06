"""
Ultron Empire — Content Generation Agent
Generates market briefs, social posts, newsletters, client messages.
"""

import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from backend.config import settings
from backend.utils.brand import BRAND_NAME, TAGLINE, WEBSITE, TELEGRAM_FOOTER
from backend.prompts.content_writer import CONTENT_WRITER_PROMPT
from backend.prompts.market_commentator import MARKET_COMMENTATOR_PROMPT

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


async def generate_morning_brief(market_data: dict = None, news: list = None, fii_dii: dict = None) -> str:
    """Generate the daily morning brief with live market data.

    If market_data/news/fii_dii are not provided, fetches live data automatically.
    """
    # Fetch live market data if not provided
    if market_data is None:
        try:
            from backend.tools.market_data import market_data_tool
            live_overview = market_data_tool.invoke({"indicator": "overview"})
        except Exception as e:
            logger.warning(f"Failed to fetch live market data: {e}")
            live_overview = "Market data unavailable"
    else:
        live_overview = str(market_data)

    context = (
        f"Live Market Data:\n{live_overview}\n\n"
        f"Top News: {news or 'Use your knowledge of current events'}\n"
        f"FII/DII Flows: {fii_dii or 'Include if available from market data above'}"
    )

    system_prompt = (
        CONTENT_SYSTEM + "\n\n"
        + MARKET_COMMENTATOR_PROMPT + "\n\n"
        "Generate a morning market brief for Telegram using the structure:\n"
        "☀️ Global Cues → India Pre-Market → FII/DII → Nifty Pulse → Events Today → Ultron's Take\n\n"
        "Use the live market data provided. Format with emojis and bold headings for Telegram."
    )

    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=context),
    ])
    return response.content


async def generate_social_post(
    topic: str,
    data: dict = None,
    format_type: str = "instagram",
) -> str:
    """Generate an Instagram/LinkedIn/blog/WhatsApp post.

    Args:
        topic: The topic for the post
        data: Optional data to include
        format_type: One of "instagram", "linkedin", "blog", "whatsapp"
    """
    format_instructions = ""
    if format_type == "whatsapp":
        format_instructions = (
            "\n\n**WhatsApp Group Message:**\n"
            "- Short, punchy, emoji-rich\n"
            "- Under 500 characters\n"
            '- End with "— Ultron | PMS Sahi Hai"'
        )
    elif format_type == "blog":
        format_instructions = (
            "\n\nGenerate a blog post format:\n"
            "- Compelling headline\n"
            "- 3-5 sections with subheadings\n"
            "- 800-1200 words\n"
            "- Data-driven insights throughout\n"
            "- SEO-friendly with natural keyword usage\n"
            "- End with CTA to visit pmssahihai.com"
        )
    else:
        # Use the detailed format instructions from content_writer prompt
        format_instructions = ""

    system_prompt = (
        CONTENT_SYSTEM + "\n\n"
        + CONTENT_WRITER_PROMPT + "\n\n"
        + format_instructions + "\n\n"
        f"Generate a {format_type} post. Follow the {format_type.title()} format instructions exactly."
    )

    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
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
