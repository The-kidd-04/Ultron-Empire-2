"""Ultron — Telegram notification delivery."""

import logging
import asyncio
from backend.alerts.telegram_bot import send_alert_to_telegram
from backend.alerts.formatter import format_telegram_alert

logger = logging.getLogger(__name__)


def send_telegram(priority: str, title: str, message: str):
    """Send formatted alert to Telegram."""
    formatted = format_telegram_alert(priority, title, message)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(send_alert_to_telegram(formatted, priority))
        else:
            asyncio.run(send_alert_to_telegram(formatted, priority))
    except Exception as e:
        logger.error(f"Telegram notification failed: {e}")
