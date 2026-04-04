"""Ultron Telegram Bot — Inline Button Callback Handlers"""

from telegram import Update


async def handle_callback(update: Update, context):
    """Handle inline keyboard button callbacks."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "refresh_market":
        from telegram_bot.handlers.commands import market
        await market(update, context)
    elif data == "show_alerts":
        from backend.alerts.engine import get_recent_alerts
        alerts = get_recent_alerts(limit=5)
        if alerts:
            text = "\n\n".join(f"{'🔴' if a.priority == 'critical' else '🔵'} {a.title}" for a in alerts)
        else:
            text = "No recent alerts."
        await query.edit_message_text(text)
