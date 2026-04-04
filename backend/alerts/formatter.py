"""
Ultron Empire — Alert Message Formatter
Brand-consistent formatting for all alert channels.
"""

from backend.utils.brand import TELEGRAM_FOOTER

EMOJI_MAP = {
    "critical": "🔴",
    "important": "🟡",
    "info": "🔵",
    "client": "👤",
}


def format_telegram_alert(priority: str, title: str, message: str, category: str = "") -> str:
    """Format alert for Telegram delivery."""
    emoji = EMOJI_MAP.get(priority, "🔵")
    priority_label = priority.upper()
    cat_label = f" | {category}" if category else ""

    return (
        f"{emoji} *{priority_label}{cat_label}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*{title}*\n\n"
        f"{message}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{TELEGRAM_FOOTER}"
    )


def format_whatsapp_alert(priority: str, title: str, message: str) -> str:
    """Format alert for WhatsApp delivery (simpler formatting)."""
    emoji = EMOJI_MAP.get(priority, "🔵")
    return f"{emoji} *{title}*\n\n{message}\n\n— Ultron Empire | PMS Sahi Hai"


def format_dashboard_alert(priority: str, title: str, message: str, category: str = "") -> dict:
    """Format alert for dashboard display."""
    return {
        "priority": priority,
        "title": title,
        "message": message,
        "category": category,
        "color": {"critical": "#FF0000", "important": "#FFB800", "info": "#0066FF", "client": "#008C6F"}.get(priority, "#0066FF"),
    }
