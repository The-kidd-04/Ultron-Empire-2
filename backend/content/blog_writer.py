"""Ultron Empire — SEO Blog Post Generator"""

import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from backend.config import settings

logger = logging.getLogger(__name__)

llm = ChatAnthropic(model=settings.CLAUDE_MODEL, api_key=settings.ANTHROPIC_API_KEY, temperature=0.5, max_tokens=3000)


async def generate_blog_post(topic: str, keywords: list = None) -> str:
    kw_text = f"Target keywords: {', '.join(keywords)}" if keywords else ""
    response = await llm.ainvoke([
        SystemMessage(content=(
            "You are Ultron's content engine for PMS Sahi Hai blog (pmssahihai.com). "
            "Write SEO-optimized blog posts about PMS, AIF, wealth management. "
            "Use H2/H3 headings, data points, and natural keyword placement. "
            "Target audience: HNIs considering PMS/AIF investments."
        )),
        HumanMessage(content=f"Topic: {topic}\n{kw_text}\n\nWrite the blog post (800-1200 words)."),
    ])
    return response.content
