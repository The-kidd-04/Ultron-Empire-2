"""
Ultron Empire — Notification Orchestrator (V3 Jarvis)
Decides WHERE to send each alert based on priority, time, and context.
"""

import logging
from datetime import datetime
from backend.utils.date_utils import now_ist

logger = logging.getLogger(__name__)


class NotificationOrchestrator:
    """Smart router that decides which surfaces get each notification."""

    CHANNEL_MAP = {
        "critical": ["phone_push", "telegram", "whatsapp", "watch", "dashboard", "email"],
        "important": ["phone_push", "telegram", "dashboard"],
        "informational": ["dashboard"],
        "client": ["phone_push", "telegram", "dashboard"],
    }

    def route(self, priority: str, title: str, message: str, category: str = "", client_id: int = None) -> list:
        """Determine delivery channels and send."""
        channels = list(self.CHANNEL_MAP.get(priority, ["dashboard"]))

        # Time-based filtering (night mode: 11 PM - 7 AM IST)
        hour = now_ist().hour
        if hour >= 23 or hour < 7:
            if priority != "critical":
                channels = ["dashboard"]  # Queue for morning

        # Filter channels and send
        delivered = []
        for channel in channels:
            try:
                self._send(channel, priority, title, message, category, client_id)
                delivered.append(channel)
            except Exception as e:
                logger.error(f"Failed to send to {channel}: {e}")

        return delivered

    def _send(self, channel: str, priority: str, title: str, message: str, category: str, client_id: int):
        """Send to a specific channel."""
        if channel == "telegram":
            from backend.notifications.telegram import send_telegram
            send_telegram(priority, title, message)
        elif channel == "whatsapp":
            from backend.notifications.whatsapp import send_whatsapp
            send_whatsapp(priority, title, message)
        elif channel == "phone_push":
            from backend.notifications.push import send_push
            send_push(priority, title, message)
        elif channel == "email":
            from backend.notifications.email import send_email_alert
            send_email_alert(priority, title, message)
        elif channel == "dashboard":
            from backend.notifications.websocket import broadcast_alert
            broadcast_alert(priority, title, message, category)
        elif channel == "watch":
            from backend.notifications.push import send_push
            send_push(priority, title, message[:100])  # Short for watch

    def is_in_meeting(self) -> bool:
        """Check if Ishaan is currently in a meeting (from calendar)."""
        # Future: Check Google Calendar API
        return False


orchestrator = NotificationOrchestrator()
