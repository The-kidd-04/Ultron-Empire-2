"""Initial schema — all Ultron tables

Revision ID: 001
Revises: None
Create Date: 2026-04-04
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False, index=True),
        sa.Column("phone", sa.String(20)),
        sa.Column("email", sa.String(200)),
        sa.Column("age", sa.Integer),
        sa.Column("occupation", sa.String(200)),
        sa.Column("city", sa.String(100)),
        sa.Column("risk_profile", sa.String(20)),
        sa.Column("investment_horizon", sa.Integer),
        sa.Column("total_investable_wealth", sa.Float),
        sa.Column("current_aum_with_us", sa.Float),
        sa.Column("annual_income", sa.Float),
        sa.Column("goals", sa.JSON, default=[]),
        sa.Column("holdings", sa.JSON, default=[]),
        sa.Column("family_members", sa.JSON, default=[]),
        sa.Column("notes", sa.Text),
        sa.Column("last_review_date", sa.Date),
        sa.Column("next_review_date", sa.Date),
        sa.Column("first_investment_date", sa.Date),
        sa.Column("tags", sa.JSON, default=[]),
        sa.Column("communication_preference", sa.String(20)),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )

    op.create_table(
        "funds",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("fund_name", sa.String(300), nullable=False, index=True),
        sa.Column("fund_house", sa.String(200), index=True),
        sa.Column("category", sa.String(20), index=True),
        sa.Column("strategy", sa.String(100)),
        sa.Column("aum", sa.Float),
        sa.Column("min_investment", sa.Float),
        sa.Column("fee_structure", sa.JSON),
        sa.Column("returns_1m", sa.Float),
        sa.Column("returns_3m", sa.Float),
        sa.Column("returns_6m", sa.Float),
        sa.Column("returns_1y", sa.Float),
        sa.Column("returns_3y", sa.Float),
        sa.Column("returns_5y", sa.Float),
        sa.Column("returns_si", sa.Float),
        sa.Column("max_drawdown", sa.Float),
        sa.Column("sharpe_ratio", sa.Float),
        sa.Column("sortino_ratio", sa.Float),
        sa.Column("benchmark", sa.String(100)),
        sa.Column("benchmark_returns_1y", sa.Float),
        sa.Column("alpha_1y", sa.Float),
        sa.Column("fund_manager", sa.String(200)),
        sa.Column("inception_date", sa.Date),
        sa.Column("top_holdings", sa.JSON, default=[]),
        sa.Column("sector_allocation", sa.JSON, default={}),
        sa.Column("portfolio_turnover", sa.Float),
        sa.Column("updated_at", sa.DateTime),
    )
    op.create_index("ix_funds_category_returns", "funds", ["category", "returns_1y"])

    op.create_table(
        "market_data",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("date", sa.Date, nullable=False, unique=True, index=True),
        sa.Column("nifty_open", sa.Float),
        sa.Column("nifty_high", sa.Float),
        sa.Column("nifty_low", sa.Float),
        sa.Column("nifty_close", sa.Float),
        sa.Column("nifty_change_pct", sa.Float),
        sa.Column("nifty_pe", sa.Float),
        sa.Column("nifty_pb", sa.Float),
        sa.Column("sensex_close", sa.Float),
        sa.Column("india_vix", sa.Float),
        sa.Column("fii_buy", sa.Float),
        sa.Column("fii_sell", sa.Float),
        sa.Column("fii_net", sa.Float),
        sa.Column("dii_buy", sa.Float),
        sa.Column("dii_sell", sa.Float),
        sa.Column("dii_net", sa.Float),
        sa.Column("advances", sa.Integer),
        sa.Column("declines", sa.Integer),
        sa.Column("advance_decline_ratio", sa.Float),
        sa.Column("nifty_bank", sa.Float),
        sa.Column("nifty_it", sa.Float),
        sa.Column("nifty_pharma", sa.Float),
        sa.Column("nifty_auto", sa.Float),
        sa.Column("nifty_fmcg", sa.Float),
        sa.Column("nifty_metal", sa.Float),
        sa.Column("nifty_realty", sa.Float),
        sa.Column("nifty_energy", sa.Float),
        sa.Column("nifty_midcap150", sa.Float),
        sa.Column("nifty_smallcap250", sa.Float),
        sa.Column("us_sp500", sa.Float),
        sa.Column("us_nasdaq", sa.Float),
        sa.Column("us_10y_yield", sa.Float),
        sa.Column("dollar_index", sa.Float),
        sa.Column("crude_oil", sa.Float),
        sa.Column("gold", sa.Float),
        sa.Column("usdinr", sa.Float),
        sa.Column("created_at", sa.DateTime),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("priority", sa.String(20), index=True),
        sa.Column("category", sa.String(50)),
        sa.Column("title", sa.String(300)),
        sa.Column("message", sa.Text),
        sa.Column("event_data", sa.JSON),
        sa.Column("client_id", sa.Integer, sa.ForeignKey("clients.id"), nullable=True),
        sa.Column("delivered_via", sa.JSON, default=[]),
        sa.Column("is_read", sa.Boolean, default=False),
        sa.Column("is_actioned", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime),
    )
    op.create_index("ix_alerts_priority_created", "alerts", ["priority", "created_at"])

    op.create_table(
        "nav_history",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("fund_id", sa.Integer, sa.ForeignKey("funds.id"), index=True),
        sa.Column("date", sa.Date, index=True),
        sa.Column("nav", sa.Float),
        sa.Column("daily_change_pct", sa.Float),
        sa.Column("created_at", sa.DateTime),
    )
    op.create_unique_constraint("uq_nav_fund_date", "nav_history", ["fund_id", "date"])

    op.create_table(
        "conversation_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(50), index=True),
        sa.Column("channel", sa.String(20)),
        sa.Column("query", sa.Text),
        sa.Column("response", sa.Text),
        sa.Column("tools_used", sa.JSON, default=[]),
        sa.Column("tokens_used", sa.Integer),
        sa.Column("response_time_ms", sa.Integer),
        sa.Column("created_at", sa.DateTime),
    )

    op.create_table(
        "prediction_signals",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("date", sa.Date, nullable=False, index=True),
        sa.Column("signal_type", sa.String(50)),
        sa.Column("sector", sa.String(50)),
        sa.Column("score", sa.Float),
        sa.Column("signal", sa.String(20)),
        sa.Column("confidence", sa.String(20)),
        sa.Column("factors", sa.JSON, default={}),
        sa.Column("summary", sa.Text),
        sa.Column("created_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("prediction_signals")
    op.drop_table("conversation_logs")
    op.drop_table("nav_history")
    op.drop_table("alerts")
    op.drop_table("market_data")
    op.drop_table("funds")
    op.drop_table("clients")
