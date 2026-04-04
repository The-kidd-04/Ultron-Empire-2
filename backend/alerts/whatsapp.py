"""
Ultron Empire — WhatsApp Delivery (Gupshup API)
Sends alerts and messages via WhatsApp Business API.
"""

import logging
import httpx
from backend.config import settings

logger = logging.getLogger(__name__)


async def send_whatsapp_message(to_number: str, message: str) -> bool:
    """Send a WhatsApp message via Gupshup API."""
    if not settings.GUPSHUP_API_KEY:
        logger.warning("Gupshup API key not configured")
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.gupshup.io/wa/api/v1/msg",
                headers={"apikey": settings.GUPSHUP_API_KEY},
                data={
                    "channel": "whatsapp",
                    "source": settings.WHATSAPP_NUMBER,
                    "destination": to_number,
                    "message": message,
                    "src.name": settings.GUPSHUP_APP_NAME,
                },
                timeout=15,
            )
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent to {to_number}")
                return True
            else:
                logger.error(f"Gupshup error: {response.status_code} — {response.text}")
                return False
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return False


async def send_whatsapp_alert(message: str, severity: str = "info") -> bool:
    """Send alert to Ishaan's WhatsApp."""
    return await send_whatsapp_message(settings.WHATSAPP_NUMBER, message)
