"""
Ultron Empire — Rebalancing Alerts (Feature 1.5)
Detects portfolio drift from target allocation and suggests rebalancing.
"""

import logging
from backend.db.database import SessionLocal
from backend.db.models import Client, FundData

logger = logging.getLogger(__name__)

TARGET_ALLOCATIONS = {
    "Conservative": {"Large Cap": 40, "Debt": 35, "Fixed Income": 25},
    "Moderate": {"Multi Cap": 35, "Mid Cap": 25, "Debt": 20, "Large Cap": 20},
    "Aggressive": {"Small Cap": 30, "Mid Cap": 25, "Multi Cap": 25, "Cat III AIF": 20},
}

DRIFT_THRESHOLD = 10  # Alert if any category drifts >10% from target


def check_portfolio_drift(client_name: str) -> dict:
    """Check if client's portfolio has drifted from target allocation."""
    session = SessionLocal()
    try:
        client = session.query(Client).filter(Client.name.ilike(f"%{client_name}%")).first()
        if not client:
            return {"error": f"Client '{client_name}' not found"}

        holdings = client.holdings or []
        if not holdings:
            return {"error": "No holdings to analyze"}

        total = sum(h.get("amount", 0) for h in holdings)
        if total == 0:
            return {"error": "Zero AUM"}

        # Get current allocation by strategy
        current_alloc = {}
        for h in holdings:
            fund = session.query(FundData).filter(
                FundData.fund_name.ilike(f"%{h['product']}%")
            ).first()
            strategy = fund.strategy if fund else "Other"
            weight = (h.get("amount", 0) / total) * 100
            current_alloc[strategy] = current_alloc.get(strategy, 0) + weight

        # Compare to target
        target = TARGET_ALLOCATIONS.get(client.risk_profile or "Moderate", TARGET_ALLOCATIONS["Moderate"])
        drifts = []
        needs_rebalancing = False

        for category, target_pct in target.items():
            current_pct = current_alloc.get(category, 0)
            drift = current_pct - target_pct
            if abs(drift) > DRIFT_THRESHOLD:
                needs_rebalancing = True
                action = "Reduce" if drift > 0 else "Increase"
                drifts.append({
                    "category": category,
                    "target_pct": target_pct,
                    "current_pct": round(current_pct, 1),
                    "drift_pct": round(drift, 1),
                    "action": f"{action} by {abs(drift):.0f}% (₹{abs(drift) * total / 10000:.2f} Cr)",
                })

        return {
            "client": client.name,
            "risk_profile": client.risk_profile,
            "total_aum_cr": total,
            "current_allocation": {k: round(v, 1) for k, v in current_alloc.items()},
            "target_allocation": target,
            "drifts": drifts,
            "needs_rebalancing": needs_rebalancing,
            "recommendation": (
                "Portfolio has drifted significantly. Rebalancing recommended."
                if needs_rebalancing else "Portfolio is within target allocation. No action needed."
            ),
        }
    finally:
        session.close()
