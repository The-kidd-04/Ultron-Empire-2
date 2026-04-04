"""
Ultron Empire — Weekly Recap Worker
Generates weekly PMS performance recap on Sunday 8 PM IST.
"""

import asyncio
import logging
from workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="workers.weekly_recap.generate_and_send")
def generate_and_send():
    """Generate weekly recap and send."""
    asyncio.run(_generate_async())


async def _generate_async():
    from backend.agents.analyst import chat_with_ultron
    from backend.alerts.telegram_bot import send_alert_to_telegram

    logger.info("Generating weekly recap...")

    result = await chat_with_ultron(
        "Generate a weekly PMS performance recap for social media. Include:\n"
        "1. Top 5 performing PMS strategies this week\n"
        "2. Bottom 5 performers\n"
        "3. Nifty 50 and Nifty 500 weekly change\n"
        "4. FII/DII weekly flow summary\n"
        "5. Key events that moved markets\n"
        "6. Ultron's weekly insight\n\n"
        "Format for Instagram/LinkedIn post with relevant hashtags."
    )

    await send_alert_to_telegram(result["response"], "info")
    logger.info("Weekly recap sent!")
