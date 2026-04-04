"""Ultron — WhatsApp notification delivery via Gupshup."""

import logging
import asyncio
from backend.alerts.whatsapp import send_whatsapp_alert
from backend.alerts.formatter import format_whatsapp_alert

logger = logging.getLogger(__name__)


def send_whatsapp(priority: str, title: str, message: str):
    """Send formatted alert to WhatsApp."""
    formatted = format_whatsapp_alert(priority, title, message)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(send_whatsapp_alert(formatted, priority))
        else:
            asyncio.run(send_whatsapp_alert(formatted, priority))
    except Exception as e:
        logger.error(f"WhatsApp notification failed: {e}")
