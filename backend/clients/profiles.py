"""
Ultron Empire — Client Profile CRUD Operations
"""

import logging
from typing import Optional
from backend.db.database import SessionLocal
from backend.db.models import Client, FundData

logger = logging.getLogger(__name__)


def get_client_by_name(name: str) -> Optional[Client]:
    """Find a client by partial name match."""
    session = SessionLocal()
    try:
        return session.query(Client).filter(Client.name.ilike(f"%{name}%")).first()
    finally:
        session.close()


def get_all_clients(risk_profile: str = None) -> list:
    """Get all clients, optionally filtered by risk profile."""
    session = SessionLocal()
    try:
        q = session.query(Client)
        if risk_profile:
            q = q.filter(Client.risk_profile == risk_profile)
        return q.order_by(Client.current_aum_with_us.desc()).all()
    finally:
        session.close()


def find_clients_by_holdings(event_data: dict) -> list:
    """Find clients affected by a fund/stock event."""
    session = SessionLocal()
    try:
        fund_name = event_data.get("fund_name", "")
        stock_name = event_data.get("stock_name", "")

        affected = []
        clients = session.query(Client).all()
        for c in clients:
            for h in (c.holdings or []):
                product = h.get("product", "").lower()
                if fund_name.lower() in product or stock_name.lower() in product:
                    affected.append({"id": c.id, "name": c.name, "holding": h})
                    break
        return affected
    finally:
        session.close()


def get_client_aum_summary() -> dict:
    """Get total AUM summary across all clients."""
    session = SessionLocal()
    try:
        clients = session.query(Client).all()
        total_aum = sum(c.current_aum_with_us or 0 for c in clients)
        total_wealth = sum(c.total_investable_wealth or 0 for c in clients)
        return {
            "total_clients": len(clients),
            "total_aum": round(total_aum, 2),
            "total_addressable_wealth": round(total_wealth, 2),
            "penetration_pct": round((total_aum / total_wealth * 100) if total_wealth else 0, 1),
            "by_risk_profile": {
                "Conservative": sum(1 for c in clients if c.risk_profile == "Conservative"),
                "Moderate": sum(1 for c in clients if c.risk_profile == "Moderate"),
                "Aggressive": sum(1 for c in clients if c.risk_profile == "Aggressive"),
            },
        }
    finally:
        session.close()
