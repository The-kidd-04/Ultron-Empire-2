"""
Ultron Empire — Daily Brief Worker
Generates and sends the morning market brief at 7:30 AM IST.
"""

import asyncio
import logging
from workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="workers.daily_brief.generate_and_send")
def generate_and_send():
    """Generate morning brief and send via Telegram."""
    asyncio.run(_generate_and_send_async())


async def _generate_and_send_async():
    from backend.agents.analyst import chat_with_ultron
    from backend.alerts.telegram_bot import send_alert_to_telegram

    logger.info("Generating morning brief...")

    result = await chat_with_ultron(
        "Generate today's morning market brief. Include:\n"
        "1. Global cues (US markets, crude, gold, DXY)\n"
        "2. SGX Nifty / pre-market signals\n"
        "3. India VIX level and implication\n"
        "4. Yesterday's FII/DII flows and streak\n"
        "5. Nifty PE and where it stands vs historical average\n"
        "6. Key events today (earnings, SEBI, RBI, global)\n"
        "7. Ultron's market take for the day\n\n"
        "Format it as a Telegram message with emojis and sections."
    )

    await send_alert_to_telegram(result["response"], "info")
    logger.info("Morning brief sent!")


@app.task(name="workers.daily_brief.generate_close_summary")
def generate_close_summary():
    """Generate end-of-day market summary at 4:00 PM IST."""
    asyncio.run(_generate_close_async())


async def _generate_close_async():
    from backend.agents.analyst import chat_with_ultron
    from backend.alerts.telegram_bot import send_alert_to_telegram

    logger.info("Generating market close summary...")

    result = await chat_with_ultron(
        "Generate today's market close summary. Include:\n"
        "1. Nifty/Sensex close with change\n"
        "2. Top gaining and losing sectors\n"
        "3. FII/DII activity today\n"
        "4. Notable stock movers in PMS portfolios\n"
        "5. VIX close and what it signals\n"
        "6. Key takeaway for the day\n\n"
        "Format as a concise Telegram message."
    )

    await send_alert_to_telegram(result["response"], "info")
    logger.info("Market close summary sent!")
