"""
Ultron Empire — Scenario Simulation Engine (Feature 1.8)
Stress-tests portfolios against historical black swan events.
"""

import logging

logger = logging.getLogger(__name__)

HISTORICAL_SCENARIOS = {
    "2008_gfc": {
        "name": "2008 Global Financial Crisis",
        "nifty_drawdown": -52,
        "large_cap_impact": -50,
        "mid_cap_impact": -65,
        "small_cap_impact": -72,
        "debt_impact": -5,
        "recovery_months": 24,
    },
    "2020_covid": {
        "name": "2020 COVID Crash",
        "nifty_drawdown": -38,
        "large_cap_impact": -35,
        "mid_cap_impact": -42,
        "small_cap_impact": -48,
        "debt_impact": -3,
        "recovery_months": 12,
    },
    "2022_rate_hike": {
        "name": "2022 Global Rate Hike Sell-off",
        "nifty_drawdown": -18,
        "large_cap_impact": -15,
        "mid_cap_impact": -22,
        "small_cap_impact": -28,
        "debt_impact": -2,
        "recovery_months": 10,
    },
    "custom_20pct": {
        "name": "Custom: Nifty drops 20%",
        "nifty_drawdown": -20,
        "large_cap_impact": -18,
        "mid_cap_impact": -25,
        "small_cap_impact": -32,
        "debt_impact": -2,
        "recovery_months": 8,
    },
}

STRATEGY_TO_CATEGORY = {
    "Large Cap": "large_cap_impact",
    "Multi Cap": "large_cap_impact",
    "Flexi Cap": "large_cap_impact",
    "Mid Cap": "mid_cap_impact",
    "Small Cap": "small_cap_impact",
    "Contra": "large_cap_impact",
    "Value": "large_cap_impact",
    "Special Situations": "mid_cap_impact",
    "Multi Strategy": "large_cap_impact",
    "Performing Credit": "debt_impact",
    "PE / Growth Equity": "mid_cap_impact",
    "Long Short Equity": "debt_impact",
    "Market Neutral": "debt_impact",
    "Venture Capital": "small_cap_impact",
}


def simulate_scenario(holdings: list, scenario_key: str = "2020_covid") -> dict:
    """Simulate a historical scenario on a portfolio.

    Args:
        holdings: [{"product": "...", "amount": X, "strategy": "..."}]
        scenario_key: Key from HISTORICAL_SCENARIOS
    """
    scenario = HISTORICAL_SCENARIOS.get(scenario_key)
    if not scenario:
        return {"error": f"Unknown scenario: {scenario_key}. Available: {list(HISTORICAL_SCENARIOS.keys())}"}

    total_invested = sum(h.get("amount", 0) for h in holdings)
    results = []
    total_loss = 0

    for h in holdings:
        strategy = h.get("strategy", "Multi Cap")
        impact_key = STRATEGY_TO_CATEGORY.get(strategy, "large_cap_impact")
        impact_pct = scenario[impact_key]
        amount = h.get("amount", 0)
        loss = amount * (impact_pct / 100)
        post_crash = amount + loss

        results.append({
            "product": h.get("product", "Unknown"),
            "strategy": strategy,
            "pre_crash_value_cr": amount,
            "impact_pct": impact_pct,
            "loss_cr": round(abs(loss), 2),
            "post_crash_value_cr": round(post_crash, 2),
        })
        total_loss += loss

    return {
        "scenario": scenario["name"],
        "nifty_drawdown": f"{scenario['nifty_drawdown']}%",
        "portfolio_pre_crash_cr": round(total_invested, 2),
        "portfolio_post_crash_cr": round(total_invested + total_loss, 2),
        "total_loss_cr": round(abs(total_loss), 2),
        "portfolio_impact_pct": round((total_loss / total_invested) * 100, 1) if total_invested else 0,
        "estimated_recovery_months": scenario["recovery_months"],
        "fund_level_impact": results,
        "advice": f"In this scenario, your portfolio would lose ₹{abs(total_loss):.2f} Cr ({abs(total_loss/total_invested*100):.0f}%). Recovery expected in ~{scenario['recovery_months']} months." if total_invested else "",
    }
