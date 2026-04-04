"""
Ultron Empire — Prediction Agent
Runs pattern matching, momentum scoring, and probabilistic analysis.
"""

import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from backend.config import settings
from backend.prediction.momentum import get_all_sector_momentum
from backend.prediction.patterns import match_current_conditions
from backend.prediction.valuation import get_pe_percentile

logger = logging.getLogger(__name__)

llm = ChatAnthropic(
    model=settings.CLAUDE_MODEL,
    api_key=settings.ANTHROPIC_API_KEY,
    temperature=0.3,
    max_tokens=2048,
)


async def generate_prediction_report(
    nifty_pe: float = None,
    vix: float = None,
    fii_net_5d: float = None,
    crude: float = None,
) -> str:
    """Generate a comprehensive market prediction report."""
    # Gather signals
    momentum = get_all_sector_momentum()
    patterns = match_current_conditions(
        nifty_pe=nifty_pe, vix_level=vix,
        fii_net_5d=fii_net_5d, crude_price=crude,
    )
    valuation = get_pe_percentile(nifty_pe or 22.0)

    context = (
        f"Sector Momentum Signals:\n{momentum}\n\n"
        f"Pattern Matches:\n{patterns}\n\n"
        f"Valuation Analysis:\n{valuation}"
    )

    response = await llm.ainvoke([
        SystemMessage(content=(
            "You are Ultron's prediction engine for PMS Sahi Hai. "
            "Synthesize momentum, pattern, and valuation signals into actionable insights. "
            "Use probabilistic language. Never make absolute predictions. "
            "Structure: Key Signals → Pattern Analysis → Valuation Zone → Ultron's View → Action Items."
        )),
        HumanMessage(content=f"Generate prediction report from:\n{context}"),
    ])
    return response.content
