"""Backfill historical market data from yfinance."""

import logging
import yfinance as yf
from datetime import date, timedelta
from backend.db.database import SessionLocal, init_db
from backend.db.models import MarketData

logger = logging.getLogger(__name__)


def backfill(days: int = 365):
    init_db()
    session = SessionLocal()
    nifty = yf.Ticker("^NSEI")
    hist = nifty.history(period=f"{days}d")

    count = 0
    for idx, row in hist.iterrows():
        d = idx.date()
        existing = session.query(MarketData).filter(MarketData.date == d).first()
        if not existing:
            record = MarketData(
                date=d,
                nifty_open=round(row["Open"], 2),
                nifty_high=round(row["High"], 2),
                nifty_low=round(row["Low"], 2),
                nifty_close=round(row["Close"], 2),
            )
            session.add(record)
            count += 1

    session.commit()
    session.close()
    print(f"Backfilled {count} market data records")


if __name__ == "__main__":
    backfill()
