"""
Ultron Empire — Festival & Event Messaging (Feature 5.6)
Pre-built templates for Indian festivals and financial events.
"""

FESTIVAL_TEMPLATES = {
    "diwali": {
        "title": "Diwali Investment Message",
        "template": (
            "🪔 *Happy Diwali from PMS Sahi Hai!*\n\n"
            "This Diwali, light up your portfolio:\n"
            "• Gold has returned {gold_return}% this year\n"
            "• Nifty 50 has returned {nifty_return}% YTD\n"
            "• Top PMS: {top_pms} at {top_pms_return}%\n\n"
            "💡 *Ultron's Diwali Tip:* {tip}\n\n"
            "Muhurat Trading this year: {muhurat_date}\n\n"
            "Wishing you wealth, health, and happiness! 🎆\n"
            "_— Team PMS Sahi Hai_"
        ),
    },
    "dhanteras": {
        "title": "Dhanteras — Gold vs Equity",
        "template": (
            "🏆 *Dhanteras Special: Gold vs Equity*\n\n"
            "₹1 Lakh invested 10 years ago:\n"
            "• Gold: ₹{gold_value}L ({gold_cagr}% CAGR)\n"
            "• Nifty 50: ₹{nifty_value}L ({nifty_cagr}% CAGR)\n"
            "• Small Cap PMS: ₹{pms_value}L ({pms_cagr}% CAGR)\n\n"
            "💡 Both have a place in your portfolio.\n"
            "Gold for safety, equity for growth.\n\n"
            "_PMS Sahi Hai | India's 1st AI Powered PMS & AIF Marketplace_"
        ),
    },
    "new_year": {
        "title": "New Year Portfolio Resolutions",
        "template": (
            "🎉 *New Year Portfolio Resolutions 2027*\n\n"
            "✅ Review portfolio allocation quarterly\n"
            "✅ Rebalance if any category drifts >10%\n"
            "✅ Max out ₹1.25L LTCG exemption\n"
            "✅ Start SIP in at least one new fund\n"
            "✅ Get a professional PMS analysis\n\n"
            "📞 Free portfolio review: +91 7455899555\n\n"
            "_PMS Sahi Hai | Making Wealth Work Smarter_"
        ),
    },
    "tax_season": {
        "title": "Tax Saving Season (Jan-Mar)",
        "template": (
            "⏰ *Tax Saving Deadline Approaching!*\n\n"
            "Don't wait for March rush. Act now:\n"
            "• ELSS SIP: ₹12,500/month = ₹1.5L deduction\n"
            "• PMS: Tax-loss harvesting before March 31\n"
            "• AIF Cat I/II: Pass-through — check your tax implications\n\n"
            "📊 *Ultron's Tax Tip:*\n"
            "Book unrealized losses now to offset gains.\n"
            "Your ₹1.25L LTCG exemption resets April 1 — use it!\n\n"
            "📞 +91 7455899555 | info@pmssahihai.com"
        ),
    },
    "budget_day": {
        "title": "Union Budget Day Analysis",
        "template": (
            "🏛️ *Budget {year} — Instant Analysis by Ultron*\n\n"
            "Key changes for HNI investors:\n"
            "{budget_highlights}\n\n"
            "📊 *Impact on Your Portfolio:*\n"
            "{portfolio_impact}\n\n"
            "💡 *Ultron's Take:*\n"
            "{ultron_take}\n\n"
            "_PMS Sahi Hai | Your AI-Powered Wealth Advisor_"
        ),
    },
    "independence_day": {
        "title": "Independence Day — Financial Freedom",
        "template": (
            "🇮🇳 *Happy Independence Day!*\n\n"
            "True financial independence = passive income > expenses.\n\n"
            "How much do you need?\n"
            "• Monthly expense ₹2L → Need ₹4 Cr corpus at 6% yield\n"
            "• Monthly expense ₹5L → Need ₹10 Cr corpus\n\n"
            "Start your journey to financial freedom with PMS.\n"
            "Minimum investment: ₹50 Lakhs.\n\n"
            "_PMS Sahi Hai | India's 1st AI Powered PMS Marketplace_"
        ),
    },
}


def get_festival_message(festival: str, data: dict = None) -> str:
    """Get a festival message template, optionally filled with data."""
    template = FESTIVAL_TEMPLATES.get(festival.lower())
    if not template:
        return f"No template for '{festival}'. Available: {list(FESTIVAL_TEMPLATES.keys())}"

    msg = template["template"]
    if data:
        try:
            msg = msg.format(**data)
        except KeyError:
            pass  # Return template with unfilled placeholders
    return msg
