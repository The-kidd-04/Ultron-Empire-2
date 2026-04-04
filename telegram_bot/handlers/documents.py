"""Ultron Telegram Bot — Document Upload Handler"""

from telegram import Update
from backend.agents.analyst import chat_with_ultron
from telegram_bot.formatters.messages import send_safe_markdown


async def handle_document(update: Update, context):
    """Handle PDF file uploads."""
    document = update.message.document
    if not document.file_name.endswith(".pdf"):
        await update.message.reply_text("I can process PDF files (CAS, factsheets, term sheets). Please upload a PDF.")
        return

    await update.message.chat.send_action("typing")
    file = await document.get_file()
    file_path = f"/tmp/{document.file_name}"
    await file.download_to_drive(file_path)

    result = await chat_with_ultron(
        f"Uploaded PDF: {document.file_name}. Analyze it — if CAS map holdings, if factsheet extract metrics, if term sheet summarize terms."
    )
    await send_safe_markdown(update, result["response"])
