"""
Ultron Empire — Database Models
All SQLAlchemy ORM models for the application.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, JSON,
    Boolean, Text, ForeignKey, UniqueConstraint, Index,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    phone = Column(String(20))
    email = Column(String(200))
    age = Column(Integer)
    occupation = Column(String(200))
    city = Column(String(100))
    risk_profile = Column(String(20))  # Conservative, Moderate, Aggressive
    investment_horizon = Column(Integer)  # years
    total_investable_wealth = Column(Float)  # in Cr
    current_aum_with_us = Column(Float)  # in Cr
    annual_income = Column(Float)  # in Cr
    goals = Column(JSON, default=list)
    holdings = Column(JSON, default=list)
    family_members = Column(JSON, default=list)
    notes = Column(Text)
    last_review_date = Column(Date)
    next_review_date = Column(Date)
    first_investment_date = Column(Date)
    tags = Column(JSON, default=list)  # ["HNI", "NRI", "Family Office"]
    communication_preference = Column(String(20))  # WhatsApp, Email, Call
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    alerts = relationship("Alert", back_populates="client")


class FundData(Base):
    __tablename__ = "funds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_name = Column(String(300), nullable=False, index=True)
    fund_house = Column(String(200), index=True)
    category = Column(String(20), index=True)  # PMS, AIF_Cat1, AIF_Cat2, AIF_Cat3, MF
    strategy = Column(String(100))  # Multicap, Small Cap, etc.
    aum = Column(Float)  # in Cr
    min_investment = Column(Float)  # in L
    fee_structure = Column(JSON)  # {"fixed": 2, "performance": 20, "hurdle": 10}
    returns_1m = Column(Float)
    returns_3m = Column(Float)
    returns_6m = Column(Float)
    returns_1y = Column(Float)
    returns_3y = Column(Float)  # CAGR
    returns_5y = Column(Float)  # CAGR
    returns_si = Column(Float)  # Since inception CAGR
    max_drawdown = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    benchmark = Column(String(100))
    benchmark_returns_1y = Column(Float)
    alpha_1y = Column(Float)
    fund_manager = Column(String(200))
    inception_date = Column(Date)
    top_holdings = Column(JSON, default=list)
    sector_allocation = Column(JSON, default=dict)
    portfolio_turnover = Column(Float)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    nav_history = relationship("NAVHistory", back_populates="fund")

    __table_args__ = (
        Index("ix_funds_category_returns", "category", "returns_1y"),
    )


class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    nifty_open = Column(Float)
    nifty_high = Column(Float)
    nifty_low = Column(Float)
    nifty_close = Column(Float)
    nifty_change_pct = Column(Float)
    nifty_pe = Column(Float)
    nifty_pb = Column(Float)
    sensex_close = Column(Float)
    india_vix = Column(Float)
    fii_buy = Column(Float)
    fii_sell = Column(Float)
    fii_net = Column(Float)
    dii_buy = Column(Float)
    dii_sell = Column(Float)
    dii_net = Column(Float)
    advances = Column(Integer)
    declines = Column(Integer)
    advance_decline_ratio = Column(Float)
    # Sector indices
    nifty_bank = Column(Float)
    nifty_it = Column(Float)
    nifty_pharma = Column(Float)
    nifty_auto = Column(Float)
    nifty_fmcg = Column(Float)
    nifty_metal = Column(Float)
    nifty_realty = Column(Float)
    nifty_energy = Column(Float)
    nifty_midcap150 = Column(Float)
    nifty_smallcap250 = Column(Float)
    # Global
    us_sp500 = Column(Float)
    us_nasdaq = Column(Float)
    us_10y_yield = Column(Float)
    dollar_index = Column(Float)
    crude_oil = Column(Float)
    gold = Column(Float)
    usdinr = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    priority = Column(String(20), index=True)  # critical, important, info, client
    category = Column(String(50))  # sebi, market, nav, earnings, client, news
    title = Column(String(300))
    message = Column(Text)
    event_data = Column(JSON)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    delivered_via = Column(JSON, default=list)
    is_read = Column(Boolean, default=False)
    is_actioned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    client = relationship("Client", back_populates="alerts")

    __table_args__ = (
        Index("ix_alerts_priority_created", "priority", "created_at"),
    )


class NAVHistory(Base):
    __tablename__ = "nav_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey("funds.id"), index=True)
    date = Column(Date, index=True)
    nav = Column(Float)
    daily_change_pct = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    fund = relationship("FundData", back_populates="nav_history")

    __table_args__ = (
        UniqueConstraint("fund_id", "date", name="uq_nav_fund_date"),
    )


class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), index=True)
    channel = Column(String(20))  # telegram, dashboard, whatsapp
    query = Column(Text)
    response = Column(Text)
    tools_used = Column(JSON, default=list)
    tokens_used = Column(Integer)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class OwnerPortfolio(Base):
    """Ishaan's personal portfolio holdings."""
    __tablename__ = "owner_portfolio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(300), nullable=False)
    product_type = Column(String(20))  # PMS, AIF, MF, Stock, FD, Other
    amount_cr = Column(Float)
    purchase_date = Column(Date)
    current_value_cr = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class PredictionSignal(Base):
    __tablename__ = "prediction_signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    signal_type = Column(String(50))  # momentum, pattern, valuation
    sector = Column(String(50))
    score = Column(Float)  # -100 to +100
    signal = Column(String(20))  # Bullish, Bearish, Neutral
    confidence = Column(String(20))  # High, Medium, Low
    factors = Column(JSON, default=dict)
    summary = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
