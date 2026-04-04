"""Ultron — Mobile push notification delivery via Expo."""

import logging
import httpx

logger = logging.getLogger(__name__)

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


async def send_push_async(priority: str, title: str, body: str, expo_token: str = None):
    """Send push notification via Expo Push Service."""
    if not expo_token:
        logger.debug("No Expo push token configured — skipping push")
        return

    data = {
        "to": expo_token,
        "title": f"{'🔴' if priority == 'critical' else '🟡' if priority == 'important' else '🔵'} {title}",
        "body": body[:200],
        "priority": "high" if priority == "critical" else "default",
        "sound": "default" if priority in ("critical", "important") else None,
        "channelId": priority,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(EXPO_PUSH_URL, json=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"Push sent: {title}")
            else:
                logger.error(f"Push failed: {response.text}")
    except Exception as e:
        logger.error(f"Push notification failed: {e}")


def send_push(priority: str, title: str, body: str):
    """Sync wrapper for push notification."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(send_push_async(priority, title, body))
        else:
            asyncio.run(send_push_async(priority, title, body))
    except Exception as e:
        logger.error(f"Push send failed: {e}")
