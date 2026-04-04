"""
Ultron Empire — AUM Flow Tracking
Tracks PMS/AIF industry AUM flows and trends.
"""

import logging

logger = logging.getLogger(__name__)

# Industry AUM data (approximate, from SEBI/AMFI reports)
INDUSTRY_AUM_TRENDS = {
    "pms_total_aum_cr": 2800000,  # ₹28 Lakh Cr
    "aif_total_aum_cr": 1200000,  # ₹12 Lakh Cr
    "mf_total_aum_cr": 7000000,   # ₹70 Lakh Cr
    "pms_yoy_growth": 22,  # %
    "aif_yoy_growth": 35,  # %
    "mf_yoy_growth": 28,  # %
}


def get_industry_aum_summary() -> dict:
    """Get current industry AUM snapshot."""
    return {
        "pms": {
            "total_aum_cr": INDUSTRY_AUM_TRENDS["pms_total_aum_cr"],
            "yoy_growth": INDUSTRY_AUM_TRENDS["pms_yoy_growth"],
            "trend": "Growing steadily — HNI allocation shifting from MF to PMS",
        },
        "aif": {
            "total_aum_cr": INDUSTRY_AUM_TRENDS["aif_total_aum_cr"],
            "yoy_growth": INDUSTRY_AUM_TRENDS["aif_yoy_growth"],
            "trend": "Fastest growing segment — PE/VC driving inflows",
        },
        "mf": {
            "total_aum_cr": INDUSTRY_AUM_TRENDS["mf_total_aum_cr"],
            "yoy_growth": INDUSTRY_AUM_TRENDS["mf_yoy_growth"],
            "trend": "SIP flows at all-time high — retail participation increasing",
        },
        "market_opportunity": (
            "PMS is just 4% of total MF AUM, but growing 22% YoY. "
            "Key driver: HNIs moving from direct stocks to professional management. "
            "AI-powered advisory (like Ultron) is a strong differentiator."
        ),
    }


def estimate_fund_house_flows(fund_house: str) -> dict:
    """Estimate AUM flow trends for a specific fund house."""
    from backend.db.database import SessionLocal
    from backend.db.models import FundData

    session = SessionLocal()
    try:
        funds = session.query(FundData).filter(
            FundData.fund_house.ilike(f"%{fund_house}%")
        ).all()

        total_aum = sum(f.aum or 0 for f in funds)
        strategies = list(set(f.strategy for f in funds))

        return {
            "fund_house": fund_house,
            "total_aum": total_aum,
            "fund_count": len(funds),
            "strategies": strategies,
            "note": "Detailed flow data requires SEBI monthly reports",
        }
    finally:
        session.close()
