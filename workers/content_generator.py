"""
Ultron Empire — Content Generator Worker
Generates social media content for the week (Monday 9:30 AM IST).
"""

import asyncio
import logging
from workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="workers.content_generator.generate_weekly_content")
def generate_weekly_content():
    """Generate social media content plan for the week."""
    asyncio.run(_generate_async())


async def _generate_async():
    from backend.agents.analyst import chat_with_ultron
    from backend.alerts.telegram_bot import send_alert_to_telegram
    from backend.content.content_calendar import generate_weekly_calendar

    logger.info("Generating weekly content plan...")

    calendar = generate_weekly_calendar()
    result = await chat_with_ultron(
        f"Generate social media content for this week based on this calendar:\n{calendar}\n\n"
        f"Create 1 Instagram post and 1 LinkedIn post. Include data, hashtags, and PMS Sahi Hai branding."
    )

    await send_alert_to_telegram(
        f"📝 *Weekly Content Plan Ready*\n\n{result['response'][:3000]}",
        "info"
    )
    logger.info("Weekly content generated!")
