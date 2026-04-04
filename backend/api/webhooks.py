"""
Ultron Empire — Webhooks API
Telegram and WhatsApp webhook endpoints.
"""

from fastapi import APIRouter, Request
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/telegram")
async def telegram_webhook(request: Request):
    """Receive Telegram webhook updates (for webhook mode instead of polling)."""
    try:
        data = await request.json()
        logger.info(f"Telegram webhook: {data.get('update_id', 'N/A')}")
        # In production: forward to python-telegram-bot's webhook handler
        return {"ok": True}
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return {"ok": False, "error": str(e)}


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Receive WhatsApp (Gupshup) webhook messages."""
    try:
        data = await request.json()
        logger.info(f"WhatsApp webhook received: {data}")

        # Extract message
        message_type = data.get("type", "")
        payload = data.get("payload", {})

        if message_type == "message":
            sender = payload.get("sender", {}).get("phone", "")
            text = payload.get("payload", {}).get("text", "")
            logger.info(f"WhatsApp from {sender}: {text}")

            # Process through Ultron agent
            from backend.agents.analyst import chat_with_ultron
            result = await chat_with_ultron(text, user_id=f"wa_{sender}")

            # Reply via WhatsApp
            from backend.alerts.whatsapp import send_whatsapp_message
            await send_whatsapp_message(sender, result["response"])

        return {"status": "processed"}
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        return {"status": "error", "error": str(e)}
