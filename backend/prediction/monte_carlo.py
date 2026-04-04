"""
Ultron Empire — Monte Carlo Portfolio Simulation
Runs 10,000 simulations for portfolio outcome probability.
"""

import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

# Historical return distributions (annualized) for Indian asset classes
ASSET_CLASS_PARAMS = {
    "Large Cap PMS": {"mean": 0.14, "std": 0.18, "skew": -0.3},
    "Mid Cap PMS": {"mean": 0.17, "std": 0.24, "skew": -0.4},
    "Small Cap PMS": {"mean": 0.20, "std": 0.30, "skew": -0.5},
    "Flexi Cap PMS": {"mean": 0.15, "std": 0.20, "skew": -0.35},
    "Multi Cap PMS": {"mean": 0.15, "std": 0.20, "skew": -0.35},
    "Debt AIF": {"mean": 0.10, "std": 0.04, "skew": 0.1},
    "Cat III AIF": {"mean": 0.12, "std": 0.12, "skew": -0.2},
    "Fixed Deposit": {"mean": 0.07, "std": 0.005, "skew": 0},
}


def run_monte_carlo(
    allocation: dict,
    investment_amount_cr: float,
    horizon_years: int,
    target_amount_cr: float = None,
    num_simulations: int = 10000,
) -> dict:
    """Run Monte Carlo simulation for a portfolio.

    Args:
        allocation: Dict of asset class → weight (e.g., {"Large Cap PMS": 0.4, "Debt AIF": 0.3})
        investment_amount_cr: Initial investment in crores
        horizon_years: Investment horizon in years
        target_amount_cr: Target corpus in crores (optional)
        num_simulations: Number of simulations (default 10,000)

    Returns:
        Simulation results with probability distribution.
    """
    np.random.seed(42)

    # Portfolio parameters (weighted)
    portfolio_mean = sum(
        ASSET_CLASS_PARAMS.get(ac, {"mean": 0.12})["mean"] * weight
        for ac, weight in allocation.items()
    )
    portfolio_std = sum(
        ASSET_CLASS_PARAMS.get(ac, {"std": 0.20})["std"] * weight
        for ac, weight in allocation.items()
    )

    # Run simulations
    final_values = []
    for _ in range(num_simulations):
        value = investment_amount_cr
        for year in range(horizon_years):
            annual_return = np.random.normal(portfolio_mean, portfolio_std)
            annual_return = max(annual_return, -0.50)  # Cap max annual loss at 50%
            value *= (1 + annual_return)
        final_values.append(value)

    final_values = np.array(final_values)

    # Calculate statistics
    median = round(float(np.median(final_values)), 2)
    mean = round(float(np.mean(final_values)), 2)
    p10 = round(float(np.percentile(final_values, 10)), 2)
    p25 = round(float(np.percentile(final_values, 25)), 2)
    p75 = round(float(np.percentile(final_values, 75)), 2)
    p90 = round(float(np.percentile(final_values, 90)), 2)
    prob_loss = round(float(np.mean(final_values < investment_amount_cr) * 100), 1)

    result = {
        "investment": investment_amount_cr,
        "horizon_years": horizon_years,
        "allocation": allocation,
        "expected_return_pa": round(portfolio_mean * 100, 1),
        "portfolio_risk_pa": round(portfolio_std * 100, 1),
        "median_outcome": median,
        "mean_outcome": mean,
        "best_case_p90": p90,
        "good_case_p75": p75,
        "poor_case_p25": p25,
        "worst_case_p10": p10,
        "probability_of_loss": prob_loss,
        "simulations": num_simulations,
    }

    if target_amount_cr:
        prob_target = round(float(np.mean(final_values >= target_amount_cr) * 100), 1)
        result["target_amount"] = target_amount_cr
        result["probability_of_reaching_target"] = prob_target

    return result
