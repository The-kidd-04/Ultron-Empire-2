"""Morning Brief Template"""

MORNING_BRIEF = """
☀️ *Ultron Morning Brief | {date}*
━━━━━━━━━━━━━━━━━━━━━

🌍 *Global Cues*
{global_summary}

🇮🇳 *India Pre-Market*
• SGX Nifty: {sgx_nifty} ({sgx_change})
• India VIX: {vix} ({vix_change})
• USD/INR: {usdinr}

📊 *Yesterday's Flows*
• FII: ₹{fii_net} Cr ({fii_direction})
• DII: ₹{dii_net} Cr ({dii_direction})
• {fii_streak}

📈 *Nifty Pulse*
• Nifty PE: {nifty_pe} (Avg: 20.5 | Percentile: {pe_percentile})
• 50-DMA: {nifty_50dma} | 200-DMA: {nifty_200dma}
• Market Breadth: {advance_decline}

📰 *Key Events Today*
{events_list}

🔍 *Ultron's Watch List*
{watchlist}

💡 *Ultron's Take*
{ai_commentary}

━━━━━━━━━━━━━━━━━━━━━
_PMS Sahi Hai | India's 1st AI Powered PMS & AIF Marketplace_
_www.pmssahihai.com | +91 7455899555_
"""
