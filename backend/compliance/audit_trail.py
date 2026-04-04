"""
Ultron Empire — Compliance & Audit Trail
Maintains full audit trail of all recommendations and regulatory compliance.
"""

import logging
from datetime import datetime, timezone
from backend.db.database import SessionLocal
from backend.db.models import ConversationLog

logger = logging.getLogger(__name__)


def log_recommendation(
    client_name: str,
    recommendation: str,
    rationale: str,
    fund_names: list = None,
    risk_disclosed: bool = True,
) -> dict:
    """Log a recommendation for compliance audit trail."""
    session = SessionLocal()
    try:
        log = ConversationLog(
            user_id="ishaan",
            channel="recommendation",
            query=f"Recommendation for {client_name}: {fund_names}",
            response=f"Rationale: {rationale}\nRisk disclosed: {risk_disclosed}",
            tools_used=fund_names or [],
        )
        session.add(log)
        session.commit()
        return {"status": "logged", "id": log.id}
    except Exception as e:
        session.rollback()
        logger.error(f"Audit log failed: {e}")
        return {"error": str(e)}
    finally:
        session.close()


def get_audit_trail(client_name: str = None, days: int = 90) -> list:
    """Get audit trail of recommendations."""
    from datetime import timedelta
    session = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        q = session.query(ConversationLog).filter(
            ConversationLog.channel == "recommendation",
            ConversationLog.created_at >= cutoff,
        )
        if client_name:
            q = q.filter(ConversationLog.query.ilike(f"%{client_name}%"))
        logs = q.order_by(ConversationLog.created_at.desc()).all()
        return [
            {
                "id": l.id,
                "query": l.query,
                "response": l.response,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in logs
        ]
    finally:
        session.close()


RISK_DISCLOSURE_TEXT = (
    "Disclaimer: Investments in PMS and AIF are subject to market risks. "
    "Past performance is not indicative of future results. "
    "Minimum investment: PMS ₹50L, AIF ₹1Cr. "
    "Please read all scheme-related documents carefully before investing. "
    "PMS Sahi Hai (Ultron Capital Pvt Ltd) is a SEBI-registered distributor."
)


def generate_risk_disclosure(product_type: str, amount_cr: float) -> str:
    """Generate appropriate risk disclosure for a product recommendation."""
    base = RISK_DISCLOSURE_TEXT

    if product_type == "PMS":
        base += "\nPMS investments are not liquid — typical lock-in of 1-3 years."
    elif product_type.startswith("AIF"):
        base += "\nAIF investments have longer lock-in periods (3-7 years) and limited liquidity."
        if product_type == "AIF_Cat3":
            base += "\nCategory III AIFs are taxed at fund level at maximum marginal rate."

    return base
