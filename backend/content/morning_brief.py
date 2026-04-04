"""
Ultron Empire — Morning Brief Generator
Generates the daily market brief using market data and AI analysis.
"""

import logging
from backend.agents.analyst import chat_with_ultron
from backend.utils.date_utils import format_date_ist, now_ist

logger = logging.getLogger(__name__)


async def generate_morning_brief() -> str:
    """Generate the complete morning brief."""
    today = format_date_ist(now_ist())

    result = await chat_with_ultron(
        f"Generate today's ({today}) morning market brief for Telegram. "
        f"Use the standard brief format with sections for:\n"
        f"1. Global Cues (US markets close, crude, gold, DXY, crypto)\n"
        f"2. India Pre-Market (SGX Nifty, VIX, USD/INR)\n"
        f"3. Yesterday's FII/DII Flows\n"
        f"4. Nifty Pulse (PE ratio, DMAs, breadth)\n"
        f"5. Key Events Today\n"
        f"6. Ultron's Watch List (stocks/sectors to watch)\n"
        f"7. Ultron's Take (market outlook for the day)\n\n"
        f"Use emojis, bold headings, and clean formatting for Telegram."
    )

    return result["response"]
