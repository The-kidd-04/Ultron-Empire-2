"""Ultron — Multi-surface message formatter."""

from backend.utils.brand import TELEGRAM_FOOTER

EMOJI = {"critical": "🔴", "important": "🟡", "informational": "🔵", "client": "👤"}


def format_for_telegram(priority: str, title: str, message: str) -> str:
    e = EMOJI.get(priority, "🔵")
    return f"{e} *{priority.upper()}*\n━━━━━━━━━━━━━━━━━━\n\n*{title}*\n\n{message}\n\n{TELEGRAM_FOOTER}"


def format_for_whatsapp(priority: str, title: str, message: str) -> str:
    e = EMOJI.get(priority, "🔵")
    return f"{e} *{title}*\n\n{message[:500]}\n\n— Ultron | PMS Sahi Hai"


def format_for_push(priority: str, title: str, message: str) -> dict:
    e = EMOJI.get(priority, "🔵")
    return {"title": f"{e} {title}", "body": message[:200]}


def format_for_email(priority: str, title: str, message: str) -> dict:
    e = EMOJI.get(priority, "🔵")
    return {"subject": f"{e} Ultron: {title}", "body": message}


def format_for_watch(priority: str, title: str) -> str:
    e = EMOJI.get(priority, "🔵")
    return f"{e} {title[:80]}"
