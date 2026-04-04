"""
Ultron Empire — Alert Agent
Classifies event severity and generates alert messages.
"""

import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from backend.config import settings
from backend.utils.brand import TELEGRAM_FOOTER

logger = logging.getLogger(__name__)

llm = ChatAnthropic(
    model=settings.CLAUDE_MODEL,
    api_key=settings.ANTHROPIC_API_KEY,
    temperature=0.2,
    max_tokens=1024,
)

SEVERITY_PROMPT = """You are Ultron's alert classification system for PMS Sahi Hai.

Classify the following event into one of these severity levels:
- "critical": Immediate action needed. Examples: SEBI regulatory change affecting PMS/AIF, market crash >3%, major fund house issue, client emergency.
- "important": Should know soon. Examples: FII selling >₹3000Cr, significant sector move >5%, new SEBI circular, fund manager change.
- "info": Good to know. Examples: General market news, earnings results, global macro updates.
- "client": Client-specific. Examples: NAV milestone, review due, portfolio event.

Respond with ONLY the severity level (one word)."""

ALERT_MESSAGE_PROMPT = """You are Ultron, the AI analyst for PMS Sahi Hai.

Generate a concise, professional Telegram alert message for this event.
Use the appropriate emoji and formatting:
- 🔴 for critical
- 🟡 for important
- 🔵 for info
- 👤 for client-specific

Include:
1. A clear headline
2. What happened (2-3 lines)
3. Impact on PMS Sahi Hai's business or clients
4. Your recommendation (1-2 lines)

Keep it under 500 characters. Use Markdown formatting for Telegram."""


async def classify_severity(event_type: str, event_data: dict) -> str:
    """Classify event severity using Claude."""
    try:
        event_summary = f"Event type: {event_type}\nDetails: {event_data}"
        response = await llm.ainvoke([
            SystemMessage(content=SEVERITY_PROMPT),
            HumanMessage(content=event_summary),
        ])
        severity = response.content.strip().lower()
        if severity not in ("critical", "important", "info", "client"):
            severity = "info"
        return severity
    except Exception as e:
        logger.error(f"Severity classification failed: {e}")
        return "info"


async def generate_alert_message(
    severity: str,
    event_data: dict,
    affected_clients: list = None,
) -> str:
    """Generate a branded alert message."""
    try:
        context = (
            f"Severity: {severity}\n"
            f"Event: {event_data}\n"
            f"Affected clients: {affected_clients or 'None specifically'}"
        )
        response = await llm.ainvoke([
            SystemMessage(content=ALERT_MESSAGE_PROMPT),
            HumanMessage(content=context),
        ])
        message = response.content.strip()
        return f"{message}\n\n{TELEGRAM_FOOTER}"
    except Exception as e:
        logger.error(f"Alert generation failed: {e}")
        emoji = {"critical": "🔴", "important": "🟡", "info": "🔵", "client": "👤"}.get(severity, "🔵")
        return f"{emoji} *Alert*\n{event_data.get('title', 'New event detected')}\n\n{TELEGRAM_FOOTER}"
