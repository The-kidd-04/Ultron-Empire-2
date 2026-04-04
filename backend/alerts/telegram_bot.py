"""
Ultron Empire — Telegram Alert Delivery
Sends formatted alerts to Ishaan's Telegram.
"""

import logging
import httpx
from backend.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


async def send_alert_to_telegram(message: str, severity: str = "info") -> bool:
    """Send an alert message to Ishaan's Telegram chat."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not configured")
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={
                    "chat_id": settings.TELEGRAM_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True,
                },
                timeout=10,
            )
            if response.status_code == 200:
                logger.info(f"Alert sent to Telegram (severity: {severity})")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} — {response.text}")
                return False
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False
