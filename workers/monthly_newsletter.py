"""
Ultron Empire — Monthly Newsletter Worker
Generates and sends the monthly client newsletter on the 1st of every month.
"""

import asyncio
import logging
from workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="workers.monthly_newsletter.generate_and_send")
def generate_and_send():
    """Generate monthly newsletter and send."""
    asyncio.run(_generate_async())


async def _generate_async():
    from backend.agents.analyst import chat_with_ultron
    from backend.alerts.telegram_bot import send_alert_to_telegram

    logger.info("Generating monthly newsletter...")

    result = await chat_with_ultron(
        "Generate the monthly client newsletter for PMS Sahi Hai. Include:\n"
        "1. Monthly market recap (Nifty, sectors, FII/DII summary)\n"
        "2. Top performing PMS strategies this month\n"
        "3. Fund spotlight — one fund in detail\n"
        "4. Ultron's outlook for next month\n"
        "5. Tax tip of the month\n"
        "6. Regulatory updates (if any)\n\n"
        "Format professionally for email distribution."
    )

    await send_alert_to_telegram(
        f"📰 *Monthly Newsletter Generated*\n\n{result['response'][:3000]}",
        "info"
    )
    logger.info("Monthly newsletter sent!")
