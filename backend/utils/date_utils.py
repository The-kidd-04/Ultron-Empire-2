"""
Ultron Empire — Date & Timezone Utilities
All times in IST (UTC+5:30) for Indian markets.
"""

from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

# Indian market hours
MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)


def now_ist() -> datetime:
    """Current time in IST."""
    return datetime.now(IST)


def today_ist() -> date:
    """Today's date in IST."""
    return now_ist().date()


def is_market_open() -> bool:
    """Check if Indian stock market is currently open."""
    now = now_ist()
    # Weekday check (Mon=0, Fri=4)
    if now.weekday() > 4:
        return False
    current_time = now.time()
    return MARKET_OPEN <= current_time <= MARKET_CLOSE


def is_business_hours() -> bool:
    """Check if within business hours (9 AM - 6 PM IST, Mon-Fri)."""
    now = now_ist()
    if now.weekday() > 4:
        return False
    return time(9, 0) <= now.time() <= time(18, 0)


def format_date_ist(dt: datetime | date) -> str:
    """Format date as 'Mon, 04 Apr 2026'."""
    if isinstance(dt, datetime):
        dt = dt.date()
    return dt.strftime("%a, %d %b %Y")


def format_datetime_ist(dt: datetime) -> str:
    """Format datetime as '04 Apr 2026, 10:30 AM IST'."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    ist_dt = dt.astimezone(IST)
    return ist_dt.strftime("%d %b %Y, %I:%M %p IST")


def last_trading_day() -> date:
    """Get the last trading day (skip weekends)."""
    today = today_ist()
    if today.weekday() == 0:  # Monday
        return today - timedelta(days=3)
    elif today.weekday() == 6:  # Sunday
        return today - timedelta(days=2)
    else:
        return today - timedelta(days=1)
