"""Ultron Telegram Bot — Natural Message Handler"""

from telegram import Update
from backend.agents.analyst import chat_with_ultron
from telegram_bot.formatters.messages import send_safe_markdown


async def handle_message(update: Update, context):
    """Handle natural language messages (no command prefix)."""
    query = update.message.text
    if not query:
        return
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron(query)
    await send_safe_markdown(update, result["response"])
