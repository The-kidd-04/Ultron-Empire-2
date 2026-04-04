"""Ultron Telegram Bot — Command Handlers (modularized from bot.py)"""

from telegram import Update
from backend.agents.analyst import chat_with_ultron
from backend.utils.brand import TELEGRAM_FOOTER
from telegram_bot.formatters.messages import send_safe_markdown


async def start(update: Update, context):
    welcome = (
        "🟢 *Ultron Empire* — Online\n\n"
        "Welcome back, Ishaan. I'm ready to help.\n\n"
        "Quick commands:\n"
        "/brief — Today's market brief\n"
        "/ask — Ask me anything\n"
        "/client — Client brief\n"
        "/market — Market snapshot\n"
        "/compare — Compare funds\n"
        "/news — Latest market news\n"
        "/help — All commands\n\n"
        "Or just type your question naturally.\n\n"
        f"{TELEGRAM_FOOTER}"
    )
    await send_safe_markdown(update, welcome)


async def help_command(update: Update, context):
    help_text = (
        "📋 *Ultron Commands*\n\n"
        "/ask `<question>` — Ask anything\n"
        "/brief — Morning market brief\n"
        "/client `<name>` — Client brief\n"
        "/compare `<A> vs <B>` — Compare funds\n"
        "/market — Market snapshot\n"
        "/news `<topic>` — Search news\n"
        "/alert — Recent alerts\n"
        "/predict — Market signals\n"
        "/help — This message\n\n"
        f"{TELEGRAM_FOOTER}"
    )
    await send_safe_markdown(update, help_text)


async def brief(update: Update, context):
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron(
        "Generate today's morning market brief with global cues, India VIX, FII/DII, Nifty PE, key events, and your take."
    )
    await send_safe_markdown(update, result["response"])


async def client_brief(update: Update, context):
    if not context.args:
        await update.message.reply_text("Usage: /client Rajesh Mehta")
        return
    client_name = " ".join(context.args)
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron(f"Pre-meeting brief for client {client_name}. Include portfolio, performance, concerns, talking points.")
    await send_safe_markdown(update, result["response"])


async def market(update: Update, context):
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron("Current market snapshot — Nifty, Sensex, VIX, FII/DII, sectors, global cues.")
    await send_safe_markdown(update, result["response"])


async def compare(update: Update, context):
    if not context.args or "vs" not in " ".join(context.args).lower():
        await update.message.reply_text("Usage: /compare Quant Small Cap PMS vs Stallion Asset PMS")
        return
    query = " ".join(context.args)
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron(f"Compare {query}. Side-by-side: returns, risk, fees, holdings overlap, recommendation.")
    await send_safe_markdown(update, result["response"])


async def news(update: Update, context):
    topic = " ".join(context.args) if context.args else "India PMS AIF market"
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron(f"Latest news on: {topic}. Summarize key points and PMS/AIF impact.")
    await send_safe_markdown(update, result["response"])


async def predict(update: Update, context):
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron("Current market prediction signals: sector momentum, patterns, VIX, historical matches.")
    await send_safe_markdown(update, result["response"])
