"""
Ultron Empire — Portfolio Analyzer Tool
Analyzes portfolios for overlap, concentration, risk, and optimization.
"""

from langchain_core.tools import tool
from backend.db.database import SessionLocal
from backend.db.models import Client, FundData
import logging

logger = logging.getLogger(__name__)


@tool
def portfolio_analyzer_tool(client_name: str) -> str:
    """Analyze a client's portfolio for overlap, concentration, risk, and optimization opportunities.

    Args:
        client_name: Client name to analyze portfolio for

    Returns:
        Portfolio analysis including overlap %, sector concentration,
        risk metrics, and recommendations.
    """
    session = SessionLocal()
    try:
        client = session.query(Client).filter(
            Client.name.ilike(f"%{client_name}%")
        ).first()

        if not client:
            return f"Client '{client_name}' not found."

        holdings = client.holdings or []
        if not holdings:
            return f"{client.name} has no recorded holdings."

        total_invested = sum(h.get("amount", 0) for h in holdings)

        # Look up fund details for each holding
        fund_details = []
        all_top_holdings = {}
        sector_exposure = {}

        for h in holdings:
            fund = session.query(FundData).filter(
                FundData.fund_name.ilike(f"%{h['product']}%")
            ).first()

            weight = (h["amount"] / total_invested * 100) if total_invested > 0 else 0

            if fund:
                fund_details.append({
                    "name": fund.fund_name,
                    "amount": h["amount"],
                    "weight": weight,
                    "returns_1y": fund.returns_1y,
                    "max_drawdown": fund.max_drawdown,
                    "sharpe": fund.sharpe_ratio,
                    "strategy": fund.strategy,
                    "top_holdings": fund.top_holdings or [],
                    "sector_allocation": fund.sector_allocation or {},
                })

                # Track stock overlap
                for stock in (fund.top_holdings or [])[:10]:
                    all_top_holdings[stock] = all_top_holdings.get(stock, 0) + 1

                # Track sector exposure
                for sector, pct in (fund.sector_allocation or {}).items():
                    weighted_pct = pct * weight / 100
                    sector_exposure[sector] = sector_exposure.get(sector, 0) + weighted_pct
            else:
                fund_details.append({
                    "name": h["product"],
                    "amount": h["amount"],
                    "weight": weight,
                    "returns_1y": None,
                    "max_drawdown": None,
                    "sharpe": None,
                    "strategy": "Unknown",
                    "top_holdings": [],
                    "sector_allocation": {},
                })

        # Build analysis
        result = f"📊 PORTFOLIO ANALYSIS: {client.name}\n"
        result += f"Total Invested: ₹{total_invested} Cr\n"
        result += f"Risk Profile: {client.risk_profile}\n\n"

        # Holdings breakdown
        result += "📋 HOLDINGS BREAKDOWN:\n"
        for fd in fund_details:
            ret = f"{fd['returns_1y']:+.1f}%" if fd["returns_1y"] else "N/A"
            result += f"  • {fd['name']}: ₹{fd['amount']} Cr ({fd['weight']:.0f}%) — 1Y: {ret}\n"

        # Stock overlap
        overlapping = {k: v for k, v in all_top_holdings.items() if v > 1}
        if overlapping:
            result += f"\n⚠️ STOCK OVERLAP ({len(overlapping)} stocks in multiple funds):\n"
            for stock, count in sorted(overlapping.items(), key=lambda x: -x[1]):
                result += f"  • {stock}: appears in {count} funds\n"
        else:
            result += "\n✅ No significant stock overlap detected.\n"

        # Sector concentration
        result += "\n📊 SECTOR EXPOSURE (weighted):\n"
        for sector, pct in sorted(sector_exposure.items(), key=lambda x: -x[1]):
            bar = "█" * int(pct / 3)
            flag = " ⚠️ HIGH" if pct > 30 else ""
            result += f"  {sector:15s}: {pct:5.1f}% {bar}{flag}\n"

        # Risk summary
        drawdowns = [fd["max_drawdown"] for fd in fund_details if fd["max_drawdown"]]
        if drawdowns:
            weighted_drawdown = sum(
                fd["max_drawdown"] * fd["weight"] / 100
                for fd in fund_details if fd["max_drawdown"]
            )
            result += f"\n📉 RISK METRICS:\n"
            result += f"  Weighted Max Drawdown: {weighted_drawdown:.1f}%\n"
            result += f"  Worst Fund Drawdown: {max(drawdowns):.1f}%\n"

        # Strategy concentration
        strategies = {}
        for fd in fund_details:
            strategies[fd["strategy"]] = strategies.get(fd["strategy"], 0) + fd["weight"]
        result += "\n🎯 STRATEGY MIX:\n"
        for strategy, weight in sorted(strategies.items(), key=lambda x: -x[1]):
            result += f"  {strategy}: {weight:.0f}%\n"

        return result
    finally:
        session.close()
