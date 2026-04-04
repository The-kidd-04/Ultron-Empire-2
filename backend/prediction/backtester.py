"""
Ultron Empire — Historical Backtesting Engine
Full backtesting with actual historical data simulation.
"""

import logging
import numpy as np
from datetime import date
from backend.db.database import SessionLocal
from backend.db.models import FundData, NAVHistory

logger = logging.getLogger(__name__)


def backtest_lumpsum(fund_id: int, investment_cr: float, start_date: date, end_date: date) -> dict:
    """Backtest a lumpsum investment over a historical period."""
    session = SessionLocal()
    try:
        fund = session.query(FundData).get(fund_id)
        if not fund:
            return {"error": "Fund not found"}

        navs = (
            session.query(NAVHistory)
            .filter(NAVHistory.fund_id == fund_id)
            .filter(NAVHistory.date.between(start_date, end_date))
            .order_by(NAVHistory.date)
            .all()
        )

        if len(navs) < 2:
            # Fall back to CAGR-based simulation
            years = (end_date - start_date).days / 365.25
            cagr = (fund.returns_5y or fund.returns_3y or fund.returns_1y or 12) / 100
            final_value = investment_cr * ((1 + cagr) ** years)

            return {
                "fund": fund.fund_name,
                "strategy": fund.strategy,
                "investment": investment_cr,
                "period_years": round(years, 1),
                "final_value": round(final_value, 2),
                "total_return_pct": round((final_value / investment_cr - 1) * 100, 1),
                "cagr_used": round(cagr * 100, 1),
                "max_drawdown": fund.max_drawdown,
                "data_source": "estimated_from_cagr",
            }

        start_nav = navs[0].nav
        end_nav = navs[-1].nav
        total_return = (end_nav / start_nav - 1) * 100
        final_value = investment_cr * (end_nav / start_nav)
        years = (navs[-1].date - navs[0].date).days / 365.25
        cagr = ((end_nav / start_nav) ** (1 / years) - 1) * 100 if years > 0 else 0

        # Calculate max drawdown from NAV history
        peak = navs[0].nav
        max_dd = 0
        for nav in navs:
            if nav.nav > peak:
                peak = nav.nav
            dd = (nav.nav - peak) / peak * 100
            if dd < max_dd:
                max_dd = dd

        return {
            "fund": fund.fund_name,
            "strategy": fund.strategy,
            "investment": investment_cr,
            "period_years": round(years, 1),
            "start_nav": start_nav,
            "end_nav": end_nav,
            "final_value": round(final_value, 2),
            "total_return_pct": round(total_return, 1),
            "cagr": round(cagr, 1),
            "max_drawdown": round(max_dd, 1),
            "data_points": len(navs),
            "data_source": "actual_nav",
        }
    finally:
        session.close()


def backtest_sip(fund_id: int, monthly_sip: float, start_date: date, end_date: date) -> dict:
    """Backtest SIP investment over a historical period."""
    session = SessionLocal()
    try:
        fund = session.query(FundData).get(fund_id)
        if not fund:
            return {"error": "Fund not found"}

        years = (end_date - start_date).days / 365.25
        months = int(years * 12)
        cagr = (fund.returns_5y or fund.returns_3y or fund.returns_1y or 12) / 100
        monthly_rate = cagr / 12

        total_invested = monthly_sip * months
        fv = monthly_sip * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        wealth_gain = fv - total_invested

        return {
            "fund": fund.fund_name,
            "strategy": fund.strategy,
            "monthly_sip": monthly_sip,
            "period_months": months,
            "total_invested": round(total_invested, 2),
            "final_value": round(fv, 2),
            "wealth_gain": round(wealth_gain, 2),
            "xirr_estimate": round(cagr * 100, 1),
            "data_source": "estimated_from_cagr",
        }
    finally:
        session.close()


def compare_backtests(fund_ids: list, investment_cr: float, years: int = 5) -> list:
    """Compare backtest results across multiple funds."""
    today = date.today()
    start = date(today.year - years, today.month, today.day)
    results = []
    for fid in fund_ids:
        bt = backtest_lumpsum(fid, investment_cr, start, today)
        if "error" not in bt:
            results.append(bt)
    return sorted(results, key=lambda x: x.get("final_value", 0), reverse=True)
