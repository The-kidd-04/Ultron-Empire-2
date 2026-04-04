"""
Ultron Empire — Business Analytics Dashboard
Tracks AUM, revenue, client concentration, and growth metrics.
"""

import logging
from backend.db.database import SessionLocal
from backend.db.models import Client, FundData

logger = logging.getLogger(__name__)


def get_business_dashboard() -> dict:
    """Get comprehensive business metrics for Ishaan."""
    session = SessionLocal()
    try:
        clients = session.query(Client).all()
        funds = session.query(FundData).all()

        total_aum = sum(c.current_aum_with_us or 0 for c in clients)
        total_wealth = sum(c.total_investable_wealth or 0 for c in clients)

        # Client concentration
        client_aums = sorted(
            [(c.name, c.current_aum_with_us or 0) for c in clients],
            key=lambda x: -x[1]
        )
        top3_aum = sum(a for _, a in client_aums[:3])
        concentration_risk = (top3_aum / total_aum * 100) if total_aum > 0 else 0

        # Revenue estimation (approximate trail income)
        # PMS trail: ~0.5-1% of AUM annually
        estimated_annual_trail = total_aum * 0.0075  # 0.75% average

        # Product mix
        product_mix = {}
        for c in clients:
            for h in (c.holdings or []):
                product = h.get("product", "Unknown")
                amount = h.get("amount", 0)
                product_mix[product] = product_mix.get(product, 0) + amount

        # Risk profile distribution
        risk_dist = {}
        for c in clients:
            profile = c.risk_profile or "Unknown"
            risk_dist[profile] = risk_dist.get(profile, 0) + 1

        # City distribution
        city_dist = {}
        for c in clients:
            city = c.city or "Unknown"
            city_dist[city] = city_dist.get(city, 0) + 1

        return {
            "total_clients": len(clients),
            "total_aum_cr": round(total_aum, 2),
            "total_addressable_wealth_cr": round(total_wealth, 2),
            "wallet_share_pct": round((total_aum / total_wealth * 100) if total_wealth > 0 else 0, 1),
            "avg_aum_per_client_cr": round(total_aum / max(len(clients), 1), 2),
            "estimated_annual_trail_cr": round(estimated_annual_trail, 2),
            "estimated_monthly_trail_cr": round(estimated_annual_trail / 12, 2),
            "client_concentration": {
                "top3_pct": round(concentration_risk, 1),
                "risk_level": "High" if concentration_risk > 60 else "Moderate" if concentration_risk > 40 else "Low",
                "top3": client_aums[:3],
            },
            "product_mix": dict(sorted(product_mix.items(), key=lambda x: -x[1])),
            "risk_profile_distribution": risk_dist,
            "city_distribution": city_dist,
            "fund_universe_size": len(funds),
        }
    finally:
        session.close()


def get_growth_metrics() -> dict:
    """Track AUM growth and client acquisition."""
    session = SessionLocal()
    try:
        clients = session.query(Client).order_by(Client.first_investment_date).all()

        # Clients by year
        by_year = {}
        for c in clients:
            if c.first_investment_date:
                year = c.first_investment_date.year
                by_year.setdefault(year, {"count": 0, "aum": 0})
                by_year[year]["count"] += 1
                by_year[year]["aum"] += c.current_aum_with_us or 0

        return {
            "clients_by_year": by_year,
            "total_clients": len(clients),
            "note": "For detailed growth tracking, update client data regularly",
        }
    finally:
        session.close()
