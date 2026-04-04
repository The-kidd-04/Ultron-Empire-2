"""Ultron Empire — WhatsApp Reply Drafter"""

from backend.agents.content_agent import generate_client_message


async def draft_whatsapp_reply(client_name: str, context: str, tone: str = "warm") -> str:
    return await generate_client_message(client_name=client_name, context=context, tone=tone)
