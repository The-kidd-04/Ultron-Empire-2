"""Ultron Telegram Bot — Voice Message Handler"""

from telegram import Update
from backend.voice.transcriber import transcribe_voice
from backend.agents.analyst import chat_with_ultron
from telegram_bot.formatters.messages import send_safe_markdown


async def handle_voice(update: Update, context):
    """Handle voice messages — transcribe then process."""
    voice = update.message.voice
    file = await voice.get_file()
    file_path = f"/tmp/voice_{update.message.message_id}.ogg"
    await file.download_to_drive(file_path)

    await update.message.chat.send_action("typing")

    # Transcribe
    text = await transcribe_voice(file_path)
    if text.startswith("Transcription failed") or text.startswith("Voice transcription requires"):
        await update.message.reply_text(text)
        return

    await update.message.reply_text(f"🎤 Heard: _{text}_", parse_mode="Markdown")

    # Process transcribed text
    result = await chat_with_ultron(text)
    await send_safe_markdown(update, result["response"])
