"""
Ultron Empire — Tool Tests
Tests for individual agent tools.
"""

import pytest
from backend.db.models import FundData, Client, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def seeded_db():
    """Create and seed a test database."""
    engine = create_engine("sqlite:///test_tools.db")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Add test fund
    fund = FundData(
        fund_name="Test PMS Fund",
        fund_house="Test House",
        category="PMS",
        strategy="Multi Cap",
        aum=1000,
        min_investment=50,
        returns_1y=25.0,
        returns_3y=20.0,
        returns_5y=18.0,
        max_drawdown=15.0,
        sharpe_ratio=1.2,
        benchmark="Nifty 500",
        benchmark_returns_1y=22.0,
        alpha_1y=3.0,
        fund_manager="Test Manager",
        top_holdings=["Stock A", "Stock B", "Stock C"],
        sector_allocation={"Banking": 30, "IT": 25},
        fee_structure={"fixed": 2.0, "performance": 15, "hurdle": 10},
    )
    session.add(fund)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


def test_calculator_cagr():
    """Test CAGR calculation."""
    from backend.tools.calculator import calculator_tool
    result = calculator_tool.invoke({
        "calculation": "cagr",
        "principal": 1.0,
        "target_amount": 2.0,
        "years": 5,
    })
    assert "CAGR" in result
    assert "14.87" in result  # ~14.87% CAGR to double in 5 years


def test_calculator_future_value():
    """Test future value calculation."""
    from backend.tools.calculator import calculator_tool
    result = calculator_tool.invoke({
        "calculation": "future_value",
        "principal": 1.0,
        "rate": 15,
        "years": 10,
    })
    assert "Future Value" in result


def test_calculator_rule_of_72():
    """Test rule of 72."""
    from backend.tools.calculator import calculator_tool
    result = calculator_tool.invoke({
        "calculation": "rule_of_72",
        "rate": 12,
    })
    assert "6.0 years" in result
