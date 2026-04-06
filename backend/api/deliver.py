"""
Ultron Empire — Deliver API
POST /deliver — Generate full analysis and send it via Telegram/Email.
Designed for ElevenLabs voice agent to trigger deliveries.
"""

import logging
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from backend.agents.analyst import chat_with_ultron
from backend.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class DeliverRequest(BaseModel):
    subject: str  # fund name, stock name, or topic
    analysis_type: str = "full"  # "full", "quick", "comparison"
    deliver_via: str = "telegram"  # "telegram", "email", "all"
    compare_with: Optional[str] = None  # for comparisons


async def _generate_and_send(subject: str, analysis_type: str, deliver_via: str, compare_with: str = None):
    """Background task: generate analysis and deliver it."""
    try:
        # Build the prompt based on analysis type
        if analysis_type == "comparison" and compare_with:
            prompt = (
                f"Generate an EXHAUSTIVE HEAD-TO-HEAD comparison of {subject} vs {compare_with}.\n\n"
                f"SIDE-BY-SIDE TABLE for:\n"
                f"- Category, Strategy, Fund House, Fund Manager\n"
                f"- AUM, Inception Date, Min Investment\n"
                f"- Returns: 1M, 3M, 6M, 1Y, 2Y, 3Y, 5Y (both funds side by side)\n"
                f"- Risk: Max Drawdown, Sharpe, Sortino, Alpha, Beta, Volatility\n"
                f"- Fees: Fixed fee, Performance fee, Hurdle rate, Total cost on 1Cr over 5Y\n"
                f"- Top 10 holdings of each fund\n"
                f"- Holdings overlap percentage\n"
                f"- Sector allocation comparison\n"
                f"- Market cap split (large/mid/small)\n"
                f"- Performance during 2020 crash and 2022 correction\n"
                f"- Fund manager experience and style difference\n\n"
                f"THEN:\n"
                f"- Which fund for Conservative investor? Why?\n"
                f"- Which fund for Aggressive investor? Why?\n"
                f"- Can you hold both? Portfolio split suggestion\n"
                f"- Clear WINNER pick with reasoning\n"
                f"- Fee-adjusted returns comparison over 5 years\n\n"
                f"Use all tools. Every number must be specific. No vague answers."
            )
        elif analysis_type == "quick":
            prompt = (
                f"Quick analysis of {subject}. "
                f"Key metrics, recent performance, and one-line verdict. Keep it under 200 words."
            )
        else:
            prompt = (
                f"Generate the MOST COMPREHENSIVE, EXHAUSTIVE analysis report possible on {subject}. "
                f"Leave NOTHING out. I need to make an investment decision based on this.\n\n"
                f"SECTION 1 — OVERVIEW\n"
                f"- What exactly is this fund/stock? Full name, category, sub-category\n"
                f"- Fund house / Company background and reputation\n"
                f"- Fund manager name, experience, previous track record, investment philosophy\n"
                f"- Investment strategy in detail (growth/value/momentum/quant/etc)\n"
                f"- AUM (assets under management) and growth trend\n"
                f"- Inception date and how long it's been running\n"
                f"- Minimum investment amount\n"
                f"- Benchmark index used\n\n"
                f"SECTION 2 — PERFORMANCE (use exact numbers)\n"
                f"- Returns: 1 Month, 3 Month, 6 Month, 1 Year, 2 Year, 3 Year, 5 Year, Since Inception\n"
                f"- Compare each period vs benchmark returns side-by-side\n"
                f"- Best year return and worst year return\n"
                f"- Rolling returns consistency (how often beats benchmark)\n"
                f"- Performance during market crashes (2020 COVID, 2022 correction)\n"
                f"- Current NAV and recent NAV trend\n\n"
                f"SECTION 3 — RISK ANALYSIS\n"
                f"- Maximum Drawdown (worst peak-to-trough fall) with dates\n"
                f"- Sharpe Ratio (risk-adjusted return)\n"
                f"- Sortino Ratio (downside risk-adjusted return)\n"
                f"- Standard Deviation / Volatility\n"
                f"- Beta (sensitivity to market moves)\n"
                f"- Alpha generated over 1Y, 3Y, 5Y vs benchmark\n"
                f"- Value at Risk (VaR) — how much could you lose in worst month\n"
                f"- Recovery time — how fast it recovers from drawdowns\n"
                f"- Downside capture ratio\n\n"
                f"SECTION 4 — PORTFOLIO DEEP DIVE\n"
                f"- Top 10-15 stock holdings with exact weight percentages\n"
                f"- Sector allocation with percentages (Banking, IT, Pharma, Auto, etc)\n"
                f"- Market cap allocation (Large cap %, Mid cap %, Small cap %)\n"
                f"- Portfolio concentration — top 5 holdings as % of total\n"
                f"- Portfolio turnover ratio (how frequently stocks are changed)\n"
                f"- Cash holding percentage\n"
                f"- Number of stocks in portfolio\n"
                f"- Any notable recent additions or exits\n\n"
                f"SECTION 5 — KEY STOCK ANALYSIS (for top 5 holdings)\n"
                f"- For each top holding: current price, 52-week high/low, PE ratio\n"
                f"- Why the fund manager holds this stock\n"
                f"- Recent news or events affecting these stocks\n"
                f"- Earnings growth trend of top holdings\n\n"
                f"SECTION 6 — FEE STRUCTURE & COSTS\n"
                f"- Management fee (fixed fee) percentage\n"
                f"- Performance fee percentage and hurdle rate\n"
                f"- Entry/exit load\n"
                f"- Lock-in period if any\n"
                f"- Total cost impact: ₹1 Cr invested, how much goes to fees in Year 1 and Year 5\n"
                f"- Fee comparison vs similar funds\n\n"
                f"SECTION 7 — COMPETITIVE COMPARISON\n"
                f"- Compare with 2-3 similar funds in same category\n"
                f"- Where does it rank in its category by 1Y and 3Y returns\n"
                f"- Advantages over competitors\n"
                f"- Disadvantages vs competitors\n\n"
                f"SECTION 8 — MARKET CONTEXT & TIMING\n"
                f"- Current market conditions (Nifty PE, VIX level, FII/DII flows)\n"
                f"- Is this a good time to enter this fund? Why?\n"
                f"- Sector outlook for the fund's major sectors\n"
                f"- How does current market cycle affect this fund\n\n"
                f"SECTION 9 — SUITABILITY & RECOMMENDATION\n"
                f"- Ideal investor profile (age, risk appetite, investment horizon)\n"
                f"- Minimum recommended investment horizon\n"
                f"- Ideal allocation percentage in a portfolio\n"
                f"- Who should NOT invest in this\n"
                f"- Tax implications (LTCG/STCG rates, tax harvesting opportunities)\n"
                f"- SEBI compliance status\n\n"
                f"SECTION 10 — RISKS & RED FLAGS\n"
                f"- Key risks specific to this fund/stock\n"
                f"- Concentration risk\n"
                f"- Fund manager risk (key person dependency)\n"
                f"- Sector-specific risks\n"
                f"- Regulatory risks\n"
                f"- Liquidity risk\n"
                f"- Any controversies or concerns\n\n"
                f"SECTION 11 — ULTRON'S FINAL VERDICT\n"
                f"- Clear BUY / HOLD / AVOID rating\n"
                f"- Confidence level (High / Medium / Low)\n"
                f"- One-paragraph summary of why\n"
                f"- Suggested entry strategy (Lumpsum / STP / SIP)\n"
                f"- Price/NAV level to watch for entry\n"
                f"- 3-year expected return range (best/base/worst case)\n\n"
                f"USE ALL AVAILABLE TOOLS. Search for latest news. Pull fund data. Check market conditions. "
                f"Include SPECIFIC NUMBERS everywhere. No vague statements. "
                f"This report should be good enough to make an investment decision."
            )

        # Generate the analysis
        result = await chat_with_ultron(prompt)
        analysis = result["response"]
        tools_used = result["tools_used"]

        # Format the message
        header = f"📊 *Ultron Analysis Report*\n{'━' * 30}\n"
        footer = (
            f"\n\n{'━' * 30}\n"
            f"_Tools used: {', '.join(tools_used) if tools_used else 'AI analysis'}_\n"
            f"_Generated by Ultron Empire — PMS Sahi Hai_\n"
            f"_pmssahihai.com | +91 7455899555_"
        )
        full_message = header + analysis + footer

        # Deliver via Telegram
        if deliver_via in ("telegram", "all"):
            await _send_telegram(full_message)

        logger.info(f"Analysis delivered via {deliver_via}: {subject}")

    except Exception as e:
        logger.error(f"Delivery failed for {subject}: {e}")
        # Try to send error notification
        try:
            await _send_telegram(f"❌ Analysis generation failed for {subject}: {str(e)[:200]}")
        except Exception:
            pass


async def _send_telegram(text: str):
    """Send a message via Telegram bot."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("Telegram delivery skipped — BOT_TOKEN or CHAT_ID not set")
        return

    import httpx

    # Split long messages (Telegram limit: 4096 chars)
    chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]

    async with httpx.AsyncClient() as client:
        for chunk in chunks:
            try:
                await client.post(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": settings.TELEGRAM_CHAT_ID,
                        "text": chunk,
                        "parse_mode": "Markdown",
                    },
                    timeout=10,
                )
            except Exception:
                # Retry without markdown if formatting fails
                await client.post(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": settings.TELEGRAM_CHAT_ID,
                        "text": chunk,
                    },
                    timeout=10,
                )


@router.post("")
async def deliver_analysis(request: DeliverRequest, background_tasks: BackgroundTasks):
    """Generate a full analysis and deliver it via Telegram/Email.

    This runs in the background so the voice agent gets an instant response
    while the analysis is being generated and sent.
    """
    background_tasks.add_task(
        _generate_and_send,
        request.subject,
        request.analysis_type,
        request.deliver_via,
        request.compare_with,
    )

    return {
        "status": "queued",
        "message": f"Full analysis of {request.subject} is being generated and will be sent to your {request.deliver_via} shortly.",
        "subject": request.subject,
        "deliver_via": request.deliver_via,
    }
