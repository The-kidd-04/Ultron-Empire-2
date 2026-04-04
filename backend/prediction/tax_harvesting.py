"""
Ultron Empire — Tax Harvesting Suggestions (Feature 1.4)
Tracks unrealized gains/losses and suggests tax-loss harvesting opportunities.
"""

import logging
from datetime import date, timedelta
from backend.db.database import SessionLocal
from backend.db.models import Client, FundData

logger = logging.getLogger(__name__)


def analyze_tax_harvesting(client_name: str) -> dict:
    """Analyze tax harvesting opportunities for a client.

    Identifies unrealized losses that can offset gains before March 31.
    """
    session = SessionLocal()
    try:
        client = session.query(Client).filter(Client.name.ilike(f"%{client_name}%")).first()
        if not client:
            return {"error": f"Client '{client_name}' not found"}

        holdings = client.holdings or []
        opportunities = []
        total_unrealized_gain = 0
        total_unrealized_loss = 0

        for h in holdings:
            fund = session.query(FundData).filter(
                FundData.fund_name.ilike(f"%{h['product']}%")
            ).first()
            if not fund:
                continue

            amount = h.get("amount", 0)
            returns_1y = fund.returns_1y or 0
            estimated_current = amount * (1 + returns_1y / 100)
            unrealized = estimated_current - amount

            if unrealized > 0:
                total_unrealized_gain += unrealized
            else:
                total_unrealized_loss += abs(unrealized)

            # Identify harvesting opportunity
            if unrealized < -0.01:  # Loss > ₹1L
                # Check holding period
                purchase_date = h.get("date", "")
                is_ltcg = False
                if purchase_date:
                    try:
                        pdate = date.fromisoformat(purchase_date)
                        is_ltcg = (date.today() - pdate).days >= 365
                    except ValueError:
                        pass

                tax_saved = abs(unrealized) * (0.125 if is_ltcg else 0.20)
                opportunities.append({
                    "fund": h["product"],
                    "invested": amount,
                    "current_value": round(estimated_current, 2),
                    "unrealized_loss": round(abs(unrealized), 2),
                    "holding_type": "LTCG" if is_ltcg else "STCG",
                    "tax_rate": "12.5%" if is_ltcg else "20%",
                    "potential_tax_saving": round(tax_saved, 4),
                    "action": f"Book loss of ₹{abs(unrealized):.2f} Cr to offset gains",
                })

        # Check if tax season is approaching
        today = date.today()
        is_tax_season = today.month in [1, 2, 3]

        return {
            "client": client.name,
            "total_unrealized_gain_cr": round(total_unrealized_gain, 2),
            "total_unrealized_loss_cr": round(total_unrealized_loss, 2),
            "net_position_cr": round(total_unrealized_gain - total_unrealized_loss, 2),
            "harvesting_opportunities": opportunities,
            "is_tax_season": is_tax_season,
            "ltcg_exemption": "₹1.25L per year (use it or lose it)",
            "recommendation": (
                f"Book ₹{total_unrealized_loss:.2f} Cr in losses to offset ₹{total_unrealized_gain:.2f} Cr in gains. "
                f"Net tax saving: ~₹{total_unrealized_loss * 0.125:.4f} Cr"
            ) if opportunities else "No tax harvesting opportunities currently.",
        }
    finally:
        session.close()
