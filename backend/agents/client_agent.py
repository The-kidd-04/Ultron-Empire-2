"""
Ultron Empire — Client Brief Generation Agent
Generates pre-meeting briefs and client communications.
"""

import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from backend.config import settings
from backend.prompts.client_communicator import CLIENT_COMMUNICATOR_PROMPT
from backend.clients.briefs import generate_client_brief

logger = logging.getLogger(__name__)

llm = ChatAnthropic(
    model=settings.CLAUDE_MODEL,
    api_key=settings.ANTHROPIC_API_KEY,
    temperature=0.3,
    max_tokens=2048,
)


async def generate_brief(client_name: str) -> str:
    """Generate a pre-meeting client brief using AI."""
    brief_data = generate_client_brief(client_name)
    if "error" in brief_data:
        return brief_data["error"]

    response = await llm.ainvoke([
        SystemMessage(content=CLIENT_COMMUNICATOR_PROMPT),
        HumanMessage(content=(
            f"Generate a pre-meeting brief for:\n{brief_data}\n\n"
            f"Include portfolio summary, performance highlights, concerns, "
            f"and suggested talking points."
        )),
    ])
    return response.content


async def draft_client_message(client_name: str, context: str, tone: str = "warm") -> str:
    """Draft a client communication message."""
    response = await llm.ainvoke([
        SystemMessage(content=CLIENT_COMMUNICATOR_PROMPT),
        HumanMessage(content=f"Draft a {tone} message to client {client_name}.\nContext: {context}"),
    ])
    return response.content
