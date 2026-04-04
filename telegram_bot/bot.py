"""
Ultron Telegram Bot — Complete Interface for Ishaan.
ALL features wired up: chat, data input, voice, predictions, content, reports.

Commands:
/start       — Welcome
/ask         — Ask Ultron anything
/brief       — Morning market brief
/client      — Client brief (/client Rajesh)
/addclient   — Add new client (guided flow)
/addholding  — Add holding to client
/compare     — Compare funds
/market      — Market snapshot
/news        — Search news
/alert       — Recent alerts
/predict     — Market signals & predictions
/portfolio   — Your personal portfolio
/addmyholding— Add to your portfolio
/content     — Generate content
/report      — Generate reports
/calc        — Financial calculator
/clients     — List all clients
/help        — All commands
"""

import logging
from datetime import date

from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters,
)
from backend.agents.analyst import chat_with_ultron
from backend.config import settings
from backend.utils.brand import TELEGRAM_FOOTER

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

AUTHORIZED_CHAT_ID = settings.TELEGRAM_CHAT_ID


def is_authorized(update: Update) -> bool:
    if not AUTHORIZED_CHAT_ID:
        return True
    return str(update.effective_chat.id) == str(AUTHORIZED_CHAT_ID)


async def safe_reply(update_or_msg, text: str):
    """Send message, split if too long, fallback from Markdown to plain."""
    msg = update_or_msg.message if hasattr(update_or_msg, 'message') else update_or_msg
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        try:
            await msg.reply_text(chunk, parse_mode="Markdown")
        except Exception:
            await msg.reply_text(chunk)


# ═══════════════════════════════════════════
# BASIC COMMANDS
# ═══════════════════════════════════════════

async def start(update: Update, context):
    if not is_authorized(update):
        await update.message.reply_text(
            f"Your Chat ID: `{update.effective_chat.id}`\nAdd this to .env as TELEGRAM_CHAT_ID to authorize.",
            parse_mode="Markdown"
        )
        return

    keyboard = [
        [InlineKeyboardButton("📊 Market", callback_data="cmd_market"),
         InlineKeyboardButton("📋 Brief", callback_data="cmd_brief")],
        [InlineKeyboardButton("👥 Clients", callback_data="cmd_clients"),
         InlineKeyboardButton("🔔 Alerts", callback_data="cmd_alerts")],
        [InlineKeyboardButton("📈 Predict", callback_data="cmd_predict"),
         InlineKeyboardButton("💼 My Portfolio", callback_data="cmd_portfolio")],
    ]

    await update.message.reply_text(
        "🟢 *Ultron Empire* — Online\n\n"
        "Welcome back, Ishaan. What do you need?\n\n"
        "Quick commands:\n"
        "/brief — Morning brief\n"
        "/client `name` — Client brief\n"
        "/market — Live market\n"
        "/compare `A vs B` — Fund comparison\n"
        "/predict — Market signals\n"
        "/portfolio — Your holdings\n"
        "/addclient — Add new client\n"
        "/addmyholding — Add to your portfolio\n"
        "/calc — Financial calculator\n"
        "/content — Generate content\n"
        "/help — All commands\n\n"
        "Or just *type naturally*.\n\n"
        f"{TELEGRAM_FOOTER}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def help_cmd(update: Update, context):
    await safe_reply(update,
        "📋 *All Ultron Commands*\n\n"
        "*💬 Chat & Analysis*\n"
        "/ask `question` — Ask anything\n"
        "/brief — Morning market brief\n"
        "/market — Live market snapshot\n"
        "/news `topic` — Search news\n"
        "/compare `A vs B` — Compare funds\n"
        "/predict — Market signals\n\n"
        "*👥 Client Management*\n"
        "/client `name` — Client brief\n"
        "/clients — List all clients\n"
        "/addclient — Add new client\n"
        "/addholding `client | fund | Cr` — Add holding\n\n"
        "*💼 Your Portfolio*\n"
        "/portfolio — View your holdings\n"
        "/addmyholding `fund | type | Cr` — Add holding\n\n"
        "*📊 Tools*\n"
        "/calc `type | params` — Calculator\n"
        "/content `type | topic` — Generate content\n"
        "/report `client name` — Generate report\n\n"
        "*🔔 Alerts*\n"
        "/alert — Recent alerts\n\n"
        "Send a *voice note* — I'll transcribe and answer.\n"
        "Send a *PDF* — I'll analyze it.\n\n"
        f"{TELEGRAM_FOOTER}"
    )


# ═══════════════════════════════════════════
# AI CHAT
# ═══════════════════════════════════════════

async def ask(update: Update, context):
    if not is_authorized(update):
        return
    query = " ".join(context.args) if context.args else update.message.text
    if not query or query.startswith("/"):
        await update.message.reply_text("Just type your question.")
        return
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron(query)
    await safe_reply(update, result["response"])


async def handle_message(update: Update, context):
    if not is_authorized(update):
        return
    await ask(update, context)


# ═══════════════════════════════════════════
# MARKET & BRIEF
# ═══════════════════════════════════════════

async def brief(update: Update, context):
    if not is_authorized(update):
        return
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron(
        "Generate today's morning market brief with global cues, VIX, FII/DII, "
        "Nifty PE, key events, and your take. Use telegram format with emojis."
    )
    await safe_reply(update, result["response"])


async def market(update: Update, context):
    if not is_authorized(update):
        return
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron("Current market snapshot — Nifty, Sensex, VIX, FII/DII, sectors, global.")
    await safe_reply(update, result["response"])


async def news(update: Update, context):
    if not is_authorized(update):
        return
    topic = " ".join(context.args) if context.args else "India PMS AIF market"
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron(f"Latest news on: {topic}. Summarize impact on PMS/AIF.")
    await safe_reply(update, result["response"])


async def compare(update: Update, context):
    if not is_authorized(update):
        return
    if not context.args or "vs" not in " ".join(context.args).lower():
        await update.message.reply_text("Usage: /compare Quant Small Cap PMS vs Stallion Asset PMS")
        return
    query = " ".join(context.args)
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron(f"Compare {query}. Side-by-side: returns, risk, fees, overlap, recommendation.")
    await safe_reply(update, result["response"])


# ═══════════════════════════════════════════
# CLIENT MANAGEMENT
# ═══════════════════════════════════════════

async def client_brief(update: Update, context):
    if not is_authorized(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /client Rajesh Mehta")
        return
    name = " ".join(context.args)
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron(
        f"Pre-meeting brief for client {name}. Portfolio, performance, concerns, talking points."
    )
    await safe_reply(update, result["response"])


async def list_clients(update: Update, context):
    if not is_authorized(update):
        return
    from backend.db.database import SessionLocal
    from backend.db.models import Client

    session = SessionLocal()
    try:
        clients = session.query(Client).order_by(Client.current_aum_with_us.desc()).all()
        if not clients:
            await update.message.reply_text("No clients yet. Use /addclient to add one.")
            return

        lines = ["👥 *Your Clients*\n"]
        total_aum = 0
        for c in clients:
            aum = c.current_aum_with_us or 0
            total_aum += aum
            review = f" | Review: {c.next_review_date}" if c.next_review_date else ""
            lines.append(f"• *{c.name}* — ₹{aum} Cr ({c.risk_profile or 'N/A'}){review}")

        lines.append(f"\n*Total AUM: ₹{total_aum:.1f} Cr* across {len(clients)} clients")
        await safe_reply(update, "\n".join(lines))
    finally:
        session.close()


async def add_client(update: Update, context):
    if not is_authorized(update):
        return

    if not context.args:
        await safe_reply(update,
            "📝 *Add New Client*\n\n"
            "Format:\n"
            "`/addclient Name | Age | City | Risk Profile | Total Wealth Cr | AUM with us Cr`\n\n"
            "Example:\n"
            "`/addclient Vikram Singh | 42 | Delhi | Aggressive | 8 | 2`\n\n"
            "Risk profiles: Conservative, Moderate, Aggressive"
        )
        return

    try:
        parts = [p.strip() for p in " ".join(context.args).split("|")]
        if len(parts) < 4:
            await update.message.reply_text("Need at least: Name | Age | City | Risk Profile")
            return

        from backend.db.database import SessionLocal
        from backend.db.models import Client

        session = SessionLocal()
        client = Client(
            name=parts[0],
            age=int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None,
            city=parts[2] if len(parts) > 2 else None,
            risk_profile=parts[3] if len(parts) > 3 else None,
            total_investable_wealth=float(parts[4]) if len(parts) > 4 else None,
            current_aum_with_us=float(parts[5]) if len(parts) > 5 else 0,
            holdings=[], goals=[], tags=[],
        )
        session.add(client)
        session.commit()
        session.refresh(client)
        session.close()

        await safe_reply(update,
            f"✅ *Client Added*\n\n"
            f"*{client.name}* (ID: {client.id})\n"
            f"Age: {client.age} | City: {client.city}\n"
            f"Risk: {client.risk_profile}\n"
            f"Wealth: ₹{client.total_investable_wealth or 0} Cr\n"
            f"AUM: ₹{client.current_aum_with_us or 0} Cr\n\n"
            f"Add holdings: `/addholding {client.name} | Fund Name | Amount Cr`"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def add_holding(update: Update, context):
    if not is_authorized(update):
        return

    if not context.args:
        await safe_reply(update,
            "📊 *Add Client Holding*\n\n"
            "Format:\n`/addholding Client Name | Fund Name | Amount in Cr`\n\n"
            "Example:\n`/addholding Rajesh Mehta | Quant Small Cap PMS | 1.5`"
        )
        return

    try:
        parts = [p.strip() for p in " ".join(context.args).split("|")]
        if len(parts) < 3:
            await update.message.reply_text("Need: Client Name | Fund Name | Amount Cr")
            return

        from backend.db.database import SessionLocal
        from backend.db.models import Client

        session = SessionLocal()
        client = session.query(Client).filter(Client.name.ilike(f"%{parts[0]}%")).first()
        if not client:
            session.close()
            await update.message.reply_text(f"Client '{parts[0]}' not found.")
            return

        holdings = list(client.holdings or [])
        holdings.append({"product": parts[1], "amount": float(parts[2]), "date": str(date.today())})
        client.holdings = holdings
        client.current_aum_with_us = sum(h.get("amount", 0) for h in holdings)
        session.commit()
        session.close()

        await safe_reply(update,
            f"✅ *Holding Added*\n\n"
            f"Client: *{client.name}*\n"
            f"Fund: {parts[1]}\nAmount: ₹{parts[2]} Cr\n"
            f"Total AUM: ₹{client.current_aum_with_us} Cr"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


# ═══════════════════════════════════════════
# ISHAAN'S OWN PORTFOLIO
# ═══════════════════════════════════════════

async def my_portfolio(update: Update, context):
    if not is_authorized(update):
        return

    from backend.db.database import SessionLocal, engine
    from backend.db.models import OwnerPortfolio, Base
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        holdings = session.query(OwnerPortfolio).order_by(OwnerPortfolio.amount_cr.desc()).all()
        if not holdings:
            await safe_reply(update,
                "💼 *Your Portfolio*\n\nNo holdings yet.\n\n"
                "Add: `/addmyholding Quant Small Cap PMS | PMS | 2.5`"
            )
            return

        total = sum(h.amount_cr or 0 for h in holdings)
        lines = ["💼 *Your Personal Portfolio*\n"]

        by_type = {}
        for h in holdings:
            by_type.setdefault(h.product_type or "Other", []).append(h)

        for ptype, items in by_type.items():
            type_total = sum(h.amount_cr or 0 for h in items)
            lines.append(f"\n*{ptype}* (₹{type_total:.1f} Cr)")
            for h in items:
                pct = (h.amount_cr / total * 100) if total > 0 else 0
                lines.append(f"  • {h.product_name}: ₹{h.amount_cr} Cr ({pct:.0f}%)")

        lines.append(f"\n*Total: ₹{total:.1f} Cr*")
        await safe_reply(update, "\n".join(lines))
    finally:
        session.close()


async def add_my_holding(update: Update, context):
    if not is_authorized(update):
        return

    if not context.args:
        await safe_reply(update,
            "💼 *Add to Your Portfolio*\n\n"
            "Format: `/addmyholding Product | Type | Amount Cr`\n\n"
            "Types: PMS, AIF, MF, Stock, FD, Other\n\n"
            "Examples:\n"
            "`/addmyholding Quant Small Cap PMS | PMS | 2.5`\n"
            "`/addmyholding HDFC Balanced Advantage | MF | 0.5`\n"
            "`/addmyholding Reliance Industries | Stock | 0.3`"
        )
        return

    try:
        parts = [p.strip() for p in " ".join(context.args).split("|")]
        if len(parts) < 3:
            await update.message.reply_text("Need: Product Name | Type | Amount Cr")
            return

        from backend.db.database import SessionLocal, engine
        from backend.db.models import OwnerPortfolio, Base
        Base.metadata.create_all(bind=engine)

        session = SessionLocal()
        holding = OwnerPortfolio(
            product_name=parts[0], product_type=parts[1],
            amount_cr=float(parts[2]), purchase_date=date.today(),
            current_value_cr=float(parts[2]),
        )
        session.add(holding)
        session.commit()
        session.close()

        await safe_reply(update,
            f"✅ *Added to Your Portfolio*\n\n"
            f"{parts[0]}\nType: {parts[1]}\nAmount: ₹{parts[2]} Cr\n\nView: /portfolio"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


# ═══════════════════════════════════════════
# PREDICTIONS
# ═══════════════════════════════════════════

async def predict(update: Update, context):
    if not is_authorized(update):
        return
    await update.message.chat.send_action("typing")
    result = await chat_with_ultron(
        "Run full prediction analysis:\n"
        "1. Get current Nifty PE and valuation zone\n"
        "2. Sector momentum signals\n"
        "3. Historical pattern matches\n"
        "4. Drawdown probability\n"
        "5. Actionable insights for PMS allocation\n\n"
        "Use all tools. Be specific."
    )
    await safe_reply(update, result["response"])


# ═══════════════════════════════════════════
# CALCULATOR
# ═══════════════════════════════════════════

async def calc(update: Update, context):
    if not is_authorized(update):
        return

    if not context.args:
        await safe_reply(update,
            "🔢 *Financial Calculator*\n\n"
            "`/calc cagr | 1 | 3 | 5` — CAGR (₹1Cr→₹3Cr in 5Y)\n"
            "`/calc future | 2 | 15 | 10` — FV (₹2Cr@15% 10Y)\n"
            "`/calc sip | 50000 | 12 | 15` — SIP maturity\n"
            "`/calc sipneeded | 5 | 15 | 15` — SIP for target\n"
            "`/calc tax | 1 | 2.5` — LTCG tax\n"
            "`/calc double | 15` — Doubling time"
        )
        return

    try:
        parts = [p.strip() for p in " ".join(context.args).split("|")]
        calc_type = parts[0].lower()
        from backend.tools.calculator import calculator_tool

        param_map = {
            "cagr": {"calculation": "cagr", "principal": float(parts[1]), "target_amount": float(parts[2]), "years": float(parts[3])},
            "future": {"calculation": "future_value", "principal": float(parts[1]), "rate": float(parts[2]), "years": float(parts[3])},
            "sip": {"calculation": "sip_future_value", "monthly_sip": float(parts[1]), "rate": float(parts[2]), "years": float(parts[3])},
            "sipneeded": {"calculation": "sip_required", "target_amount": float(parts[1]), "rate": float(parts[2]), "years": float(parts[3])},
            "tax": {"calculation": "tax_ltcg", "principal": float(parts[1]), "target_amount": float(parts[2])},
            "double": {"calculation": "rule_of_72", "rate": float(parts[1])},
        }

        if calc_type in param_map:
            result = calculator_tool.invoke(param_map[calc_type])
        else:
            result = "Unknown type. See /calc"

        await safe_reply(update, result)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}\nSee /calc for format.")


# ═══════════════════════════════════════════
# CONTENT & REPORTS
# ═══════════════════════════════════════════

async def content(update: Update, context):
    if not is_authorized(update):
        return

    if not context.args:
        keyboard = [
            [InlineKeyboardButton("📱 Instagram Post", callback_data="content_instagram")],
            [InlineKeyboardButton("💼 LinkedIn Post", callback_data="content_linkedin")],
            [InlineKeyboardButton("📰 Newsletter", callback_data="content_newsletter")],
            [InlineKeyboardButton("📝 Blog Post", callback_data="content_blog")],
        ]
        await update.message.reply_text("📝 *What content?*\n\nOr: `/content instagram top 5 PMS`",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    await update.message.chat.send_action("typing")
    result = await chat_with_ultron(f"Generate content: {' '.join(context.args)}. Match PMS Sahi Hai brand voice. Add hashtags for social.")
    await safe_reply(update, result["response"])


async def report(update: Update, context):
    if not is_authorized(update):
        return
    if not context.args:
        await safe_reply(update, "📊 *Reports*\n\n`/report Rajesh Mehta` — Client report\n`/report market` — Market outlook")
        return
    query = " ".join(context.args)
    await update.message.chat.send_action("typing")
    if query.lower() == "market":
        result = await chat_with_ultron("Comprehensive market outlook: Nifty, sectors, FII/DII, global, strategy.")
    else:
        result = await chat_with_ultron(f"Portfolio report for client {query}. Holdings, performance, risk, recommendations.")
    await safe_reply(update, result["response"])


async def alert_history(update: Update, context):
    if not is_authorized(update):
        return
    from backend.alerts.engine import get_recent_alerts
    alerts = get_recent_alerts(limit=10)
    if not alerts:
        await update.message.reply_text("No recent alerts.")
        return
    emoji = {"critical": "🔴", "important": "🟡", "info": "🔵", "client": "👤"}
    lines = ["🔔 *Recent Alerts*\n"]
    for a in alerts:
        t = a.created_at.strftime("%d %b, %I:%M %p") if a.created_at else ""
        lines.append(f"{emoji.get(a.priority, '🔵')} *{a.title}*\n{(a.message or '')[:100]}\n_{t}_\n")
    await safe_reply(update, "\n".join(lines))


# ═══════════════════════════════════════════
# VOICE & DOCUMENTS
# ═══════════════════════════════════════════

async def handle_voice(update: Update, context):
    if not is_authorized(update):
        return
    await update.message.chat.send_action("typing")
    voice = update.message.voice or update.message.audio
    file = await voice.get_file()
    path = f"/tmp/voice_{update.message.message_id}.ogg"
    await file.download_to_drive(path)

    from backend.voice.transcriber import transcribe_voice
    text = await transcribe_voice(path)
    if "failed" in text.lower() or "requires" in text.lower():
        await update.message.reply_text(f"🎤 {text}")
        return
    await update.message.reply_text(f"🎤 _Heard: {text}_", parse_mode="Markdown")
    result = await chat_with_ultron(text)
    await safe_reply(update, result["response"])


async def handle_document(update: Update, context):
    if not is_authorized(update):
        return
    doc = update.message.document
    if not doc.file_name.endswith(".pdf"):
        await update.message.reply_text("Send a PDF — CAS, factsheet, or term sheet.")
        return
    await update.message.chat.send_action("typing")
    file = await doc.get_file()
    path = f"/tmp/{doc.file_name}"
    await file.download_to_drive(path)
    result = await chat_with_ultron(f"Uploaded PDF: {doc.file_name}. Analyze it — CAS→map holdings, factsheet→metrics, term sheet→flags.")
    await safe_reply(update, result["response"])


# ═══════════════════════════════════════════
# CALLBACKS
# ═══════════════════════════════════════════

async def handle_callback(update: Update, context):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "cmd_market":
        await q.message.chat.send_action("typing")
        r = await chat_with_ultron("Current market snapshot — Nifty, Sensex, VIX, FII/DII, sectors.")
        try: await q.message.reply_text(r["response"][:4000], parse_mode="Markdown")
        except: await q.message.reply_text(r["response"][:4000])
    elif data == "cmd_brief":
        await q.message.chat.send_action("typing")
        r = await chat_with_ultron("Morning brief: global cues, VIX, FII/DII, events, take.")
        try: await q.message.reply_text(r["response"][:4000], parse_mode="Markdown")
        except: await q.message.reply_text(r["response"][:4000])
    elif data == "cmd_clients":
        from backend.db.database import SessionLocal
        from backend.db.models import Client
        s = SessionLocal()
        cs = s.query(Client).all()
        s.close()
        t = "\n".join(f"• {c.name} — ₹{c.current_aum_with_us or 0} Cr" for c in cs) or "No clients."
        try: await q.message.reply_text(f"👥 *Clients*\n\n{t}", parse_mode="Markdown")
        except: await q.message.reply_text(f"Clients\n\n{t}")
    elif data == "cmd_alerts":
        from backend.alerts.engine import get_recent_alerts
        alerts = get_recent_alerts(5)
        t = "\n".join(f"{'🔴' if a.priority=='critical' else '🔵'} {a.title}" for a in alerts) or "No alerts."
        await q.message.reply_text(t)
    elif data == "cmd_predict":
        await q.message.chat.send_action("typing")
        r = await chat_with_ultron("Prediction: valuation, momentum, patterns, drawdown. Be specific.")
        try: await q.message.reply_text(r["response"][:4000], parse_mode="Markdown")
        except: await q.message.reply_text(r["response"][:4000])
    elif data == "cmd_portfolio":
        from backend.db.database import SessionLocal, engine
        from backend.db.models import OwnerPortfolio, Base
        Base.metadata.create_all(bind=engine)
        s = SessionLocal()
        hs = s.query(OwnerPortfolio).all()
        s.close()
        if hs:
            total = sum(h.amount_cr or 0 for h in hs)
            t = "\n".join(f"• {h.product_name} ({h.product_type}): ₹{h.amount_cr} Cr" for h in hs)
            try: await q.message.reply_text(f"💼 *Your Portfolio*\n\n{t}\n\n*Total: ₹{total:.1f} Cr*", parse_mode="Markdown")
            except: await q.message.reply_text(f"Portfolio\n\n{t}\n\nTotal: {total:.1f} Cr")
        else:
            await q.message.reply_text("No holdings. Use /addmyholding")
    elif data.startswith("content_"):
        ctype = data.replace("content_", "")
        await q.message.reply_text(f"Type: `/content {ctype} your topic`", parse_mode="Markdown")


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════

async def post_init(app: Application):
    commands = [
        BotCommand("start", "Welcome & quick actions"),
        BotCommand("ask", "Ask Ultron anything"),
        BotCommand("brief", "Morning market brief"),
        BotCommand("market", "Live market snapshot"),
        BotCommand("client", "Client brief"),
        BotCommand("clients", "List all clients"),
        BotCommand("addclient", "Add new client"),
        BotCommand("addholding", "Add client holding"),
        BotCommand("compare", "Compare funds"),
        BotCommand("news", "Search news"),
        BotCommand("predict", "Market signals"),
        BotCommand("portfolio", "Your portfolio"),
        BotCommand("addmyholding", "Add to portfolio"),
        BotCommand("calc", "Calculator"),
        BotCommand("content", "Generate content"),
        BotCommand("report", "Generate report"),
        BotCommand("alert", "Recent alerts"),
        BotCommand("help", "All commands"),
    ]
    await app.bot.set_my_commands(commands)


def main():
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set.")
        return

    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    # ALL commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("brief", brief))
    app.add_handler(CommandHandler("market", market))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("compare", compare))
    app.add_handler(CommandHandler("client", client_brief))
    app.add_handler(CommandHandler("clients", list_clients))
    app.add_handler(CommandHandler("addclient", add_client))
    app.add_handler(CommandHandler("addholding", add_holding))
    app.add_handler(CommandHandler("portfolio", my_portfolio))
    app.add_handler(CommandHandler("addmyholding", add_my_holding))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("calc", calc))
    app.add_handler(CommandHandler("content", content))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("alert", alert_history))

    # Inline buttons
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Voice
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))

    # PDF
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))

    # Natural language (last)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🟢 Ultron Bot — ALL features active!")
    app.run_polling()


if __name__ == "__main__":
    main()
