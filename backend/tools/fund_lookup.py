"""
Ultron Empire — Fund Lookup Tool
Searches the PMS/AIF/MF database with filtering.
"""

from langchain_core.tools import tool
from sqlalchemy import or_

from backend.db.database import SessionLocal
from backend.db.models import FundData
from backend.utils.formatters import format_inr


@tool
def fund_lookup_tool(
    query: str,
    category: str = None,
    min_return_1y: float = None,
    max_drawdown: float = None,
    min_aum: float = None,
) -> str:
    """Search for PMS, AIF, or Mutual Fund strategies.

    Args:
        query: Fund name or search term (e.g., "Quant Small Cap" or "small cap PMS")
        category: Filter by category — "PMS", "AIF_Cat1", "AIF_Cat2", "AIF_Cat3", "MF"
        min_return_1y: Minimum 1-year return percentage
        max_drawdown: Maximum drawdown percentage (e.g., 20 means max 20% drawdown)
        min_aum: Minimum AUM in crores

    Returns:
        Formatted string with matching fund details including returns, risk metrics, and fees.
    """
    session = SessionLocal()
    try:
        q = session.query(FundData)

        # Fuzzy name search
        search_terms = query.split()
        name_filters = [FundData.fund_name.ilike(f"%{term}%") for term in search_terms]
        q = q.filter(or_(*name_filters))

        if category:
            q = q.filter(FundData.category == category)
        if min_return_1y is not None:
            q = q.filter(FundData.returns_1y >= min_return_1y)
        if max_drawdown is not None:
            q = q.filter(FundData.max_drawdown <= max_drawdown)
        if min_aum is not None:
            q = q.filter(FundData.aum >= min_aum)

        results = q.order_by(FundData.returns_1y.desc()).limit(10).all()

        if not results:
            return f"No funds found matching '{query}'. Try a broader search."

        output = []
        for fund in results:
            fee = fund.fee_structure or {}
            fee_text = f"Fixed: {fee.get('fixed', 0)}%"
            if fee.get("performance"):
                fee_text += f" + Perf: {fee['performance']}% above {fee.get('hurdle', 0)}% hurdle"

            holdings = fund.top_holdings or []
            top5 = ", ".join(holdings[:5]) if holdings else "N/A"

            def fmt(v): return f"{v:+.1f}%" if v is not None else "N/A"

            output.append(
                f"📊 {fund.fund_name} ({fund.fund_house})\n"
                f"Category: {fund.category} | Strategy: {fund.strategy}\n"
                f"AUM: ₹{fund.aum} Cr | Min Investment: ₹{fund.min_investment} L\n"
                f"Returns: 1Y: {fmt(fund.returns_1y)} | 3Y: {fmt(fund.returns_3y)} | 5Y: {fmt(fund.returns_5y)}\n"
                f"Max Drawdown: {fund.max_drawdown or 'N/A'}% | Sharpe: {fund.sharpe_ratio or 'N/A'}\n"
                f"Alpha (1Y): {fmt(fund.alpha_1y)} vs {fund.benchmark or 'N/A'}\n"
                f"Fund Manager: {fund.fund_manager or 'N/A'}\n"
                f"Fee: {fee_text}\n"
                f"Top Holdings: {top5}"
            )

        return "\n\n---\n\n".join(output)
    finally:
        session.close()
