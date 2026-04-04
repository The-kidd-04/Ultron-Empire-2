"""Ultron Telegram Bot — Message Formatters"""

from telegram import Update


async def send_safe_markdown(update: Update, text: str):
    """Send a message with Markdown, falling back to plain text if parsing fails."""
    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            chunk = text[i:i + 4000]
            try:
                await update.message.reply_text(chunk, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(chunk)
    else:
        try:
            await update.message.reply_text(text, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(text)
