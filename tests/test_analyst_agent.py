"""
Ultron Empire — Analyst Agent Tests
20+ sample queries testing the full agent pipeline.
"""

import pytest

# These tests validate tool invocation and response structure.
# Full integration tests require API keys and database.

SAMPLE_QUERIES = [
    # Fund Analysis
    "Compare Quant Small Cap PMS vs Stallion Asset Core PMS for a ₹2Cr client",
    "Which PMSes have beaten Nifty 50 over 3 years with less than 15% drawdown?",
    "Tell me about Marcellus CCP. Is it still worth recommending?",
    "What are the top 5 small cap PMS by 1-year returns?",
    "Show me PMS funds with Sharpe ratio above 1.3",
    # Client Advisory
    "My client Rajesh (55, conservative, ₹5Cr) wants to exit FD and enter PMS",
    "Get me a brief for client Rajesh Mehta",
    "Draft a WhatsApp message to Amit explaining why his PMS is down 8%",
    "Which PMS is suitable for a 35-year-old aggressive investor with ₹2Cr?",
    "What should I recommend for a client who wants regular income from ₹3Cr?",
    # Market Intelligence
    "What does the latest SEBI circular mean for PMS distributors?",
    "FII sold ₹5000Cr today. Should I be worried?",
    "Give me the current market snapshot",
    "What's the Nifty PE percentile right now?",
    "How are sector indices performing this week?",
    # Predictions
    "What's the momentum signal for banking sector?",
    "If my client invests ₹2Cr 60% equity PMS + 40% debt AIF, what are chances of reaching ₹5Cr in 10 years?",
    "How did small cap PMSes perform after the last 3 major corrections?",
    # Content
    "Create an Instagram post comparing top 5 PMSes this month",
    "Draft this week's newsletter",
    "Generate a morning brief for my WhatsApp group",
    # Calculations
    "Calculate CAGR if ₹1 Cr becomes ₹3 Cr in 5 years",
    "What SIP is needed to reach ₹5 Cr in 15 years at 15% returns?",
    "Calculate LTCG tax on ₹1 Cr invested growing to ₹2.5 Cr",
]


def test_sample_queries_count():
    """Ensure we have 20+ sample queries defined."""
    assert len(SAMPLE_QUERIES) >= 20


def test_query_categories():
    """Ensure queries span all categories."""
    categories = {
        "fund": ["Compare", "Which PMS", "Tell me about", "top 5", "Sharpe"],
        "client": ["client", "brief", "Draft", "recommend", "suitable"],
        "market": ["SEBI", "FII", "snapshot", "PE percentile", "sector"],
        "prediction": ["momentum", "invest", "corrections"],
        "content": ["Instagram", "newsletter", "morning brief"],
        "calculation": ["CAGR", "SIP", "LTCG"],
    }
    for cat, keywords in categories.items():
        found = any(
            any(kw.lower() in q.lower() for kw in keywords)
            for q in SAMPLE_QUERIES
        )
        assert found, f"Category '{cat}' not covered in sample queries"


def test_calculator_tool_directly():
    """Test calculator tool with various calculations."""
    from backend.tools.calculator import calculator_tool

    # CAGR
    result = calculator_tool.invoke({
        "calculation": "cagr", "principal": 1.0, "target_amount": 3.0, "years": 5,
    })
    assert "CAGR" in result
    assert "24.57" in result  # ~24.57% CAGR

    # Future value
    result = calculator_tool.invoke({
        "calculation": "future_value", "principal": 1.0, "rate": 15, "years": 10,
    })
    assert "Future Value" in result

    # SIP
    result = calculator_tool.invoke({
        "calculation": "sip_future_value", "monthly_sip": 50000, "rate": 12, "years": 10,
    })
    assert "SIP Future Value" in result

    # Rule of 72
    result = calculator_tool.invoke({"calculation": "rule_of_72", "rate": 12})
    assert "6.0 years" in result

    # Tax LTCG
    result = calculator_tool.invoke({
        "calculation": "tax_ltcg", "principal": 1.0, "target_amount": 2.5,
    })
    assert "LTCG" in result
    assert "12.5%" in result


def test_monte_carlo():
    """Test Monte Carlo simulation."""
    from backend.prediction.monte_carlo import run_monte_carlo

    result = run_monte_carlo(
        allocation={"Large Cap PMS": 0.4, "Mid Cap PMS": 0.3, "Debt AIF": 0.3},
        investment_amount_cr=2.0,
        horizon_years=10,
        target_amount_cr=5.0,
    )

    assert "median_outcome" in result
    assert "probability_of_reaching_target" in result
    assert result["median_outcome"] > 2.0  # Should grow
    assert 0 <= result["probability_of_reaching_target"] <= 100


def test_lead_scoring():
    """Test client lead scoring."""
    from backend.clients.scoring import calculate_lead_score

    result = calculate_lead_score(
        total_wealth_cr=10, age=45, occupation="Industrialist",
        city="Mumbai", risk_profile="Moderate", referral=True,
    )
    assert result["score"] >= 80  # Should be A+ tier
    assert "Hot Lead" in result["tier"]


def test_pe_percentile():
    """Test PE valuation analysis."""
    from backend.prediction.valuation import get_pe_percentile

    result = get_pe_percentile(22.5)
    assert result["zone"] in ["Fair Value", "Slightly Expensive"]
    assert result["percentile"] >= 50


def test_momentum_score():
    """Test momentum scoring."""
    from backend.prediction.momentum import calculate_momentum_score

    result = calculate_momentum_score(
        above_50dma=True, above_200dma=True,
        rsi=58, fii_flow_trend="accumulating",
        relative_strength="outperforming",
    )
    assert result["score"] > 50
    assert result["signal"] == "Bullish"


def test_format_inr():
    """Test Indian currency formatting."""
    from backend.utils.formatters import format_inr

    assert format_inr(2.5) == "₹2.5 Cr"
    assert format_inr(0.45) == "₹45 L"
    assert format_inr(10) == "₹10 Cr"
