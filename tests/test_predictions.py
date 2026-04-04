"""Ultron Empire — Prediction Layer Tests"""

def test_drawdown_estimation():
    from backend.prediction.drawdown import estimate_drawdown_risk
    result = estimate_drawdown_risk(nifty_pe=25.5, vix=22, fii_net_monthly=-12000)
    assert result["risk_level"] in ["High", "Moderate", "Low"]
    assert result["probability_10pct_correction"] > 0

def test_pattern_matching():
    from backend.prediction.patterns import match_current_conditions
    matches = match_current_conditions(nifty_pe=26, vix=28, fii_net_5d=-18000, crude_price=90)
    assert len(matches) >= 2  # PE + VIX + FII + Crude should trigger

def test_rate_cycle():
    from backend.prediction.rate_cycle import analyze_rate_cycle
    result = analyze_rate_cycle(current_repo_rate=6.5, last_action="pause", inflation_cpi=4.5)
    assert "next_likely_action" in result

def test_correlation_diversification():
    from backend.prediction.correlation import analyze_portfolio_diversification
    holdings = [
        {"sector_allocation": {"Banking": 30, "IT": 25, "Consumer": 20}, "weight": 50},
        {"sector_allocation": {"Industrials": 30, "Materials": 25, "Defence": 20}, "weight": 50},
    ]
    result = analyze_portfolio_diversification(holdings)
    assert result["diversification_score"] > 50
