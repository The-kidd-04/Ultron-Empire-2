"""
Ultron Empire — Social Media Content Calendar (Feature 5.5)
Plans weekly/monthly posts aligned with market events.
"""

import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

RECURRING_EVENTS = {
    "weekly": [
        {"day": "Monday", "content": "Market Week Ahead Preview", "platform": "LinkedIn"},
        {"day": "Wednesday", "content": "Mid-Week PMS Insight", "platform": "Instagram"},
        {"day": "Friday", "content": "Weekly Market Wrap", "platform": "LinkedIn + Instagram"},
        {"day": "Sunday", "content": "Weekly PMS Performance Recap", "platform": "Instagram"},
    ],
    "monthly": [
        {"day": 1, "content": "Monthly Market Recap + Newsletter", "platform": "Email + LinkedIn"},
        {"day": 10, "content": "PMS Performance Comparison", "platform": "Instagram"},
        {"day": 15, "content": "Ultron Market Outlook", "platform": "LinkedIn"},
        {"day": 25, "content": "Tax Planning Tip (if Jan-Mar)", "platform": "Instagram + WhatsApp"},
    ],
}

ANNUAL_EVENTS = [
    {"month": 1, "day": 1, "event": "New Year Investment Resolutions"},
    {"month": 1, "day": 15, "event": "Tax Saving Season Starts — PMS/ELSS Push"},
    {"month": 2, "day": 1, "event": "Union Budget Day — Instant Analysis"},
    {"month": 3, "day": 15, "event": "Tax Deadline Approaching — Last Call"},
    {"month": 3, "day": 31, "event": "Financial Year End — Tax Harvesting Reminder"},
    {"month": 4, "day": 1, "event": "New FY — Portfolio Review Month"},
    {"month": 8, "day": 15, "event": "Independence Day — Wealth Building Message"},
    {"month": 10, "day": 15, "event": "Dhanteras — Gold vs Equity Post"},
    {"month": 10, "day": 20, "event": "Diwali — Muhurat Trading + Investment Message"},
    {"month": 12, "day": 25, "event": "Year-End Portfolio Review + New Year Plans"},
]


def generate_weekly_calendar() -> list:
    """Generate this week's content calendar."""
    today = date.today()
    calendar = []
    for item in RECURRING_EVENTS["weekly"]:
        calendar.append({**item, "week_of": str(today)})

    # Check for annual events this week
    for event in ANNUAL_EVENTS:
        event_date = date(today.year, event["month"], event["day"])
        if today <= event_date <= today + timedelta(days=7):
            calendar.append({
                "day": str(event_date),
                "content": event["event"],
                "platform": "All platforms",
                "priority": "HIGH — Annual event",
            })

    return calendar


def generate_monthly_calendar() -> dict:
    """Generate this month's full content calendar."""
    today = date.today()
    monthly = RECURRING_EVENTS["monthly"]

    annual_this_month = [
        e for e in ANNUAL_EVENTS if e["month"] == today.month
    ]

    return {
        "month": today.strftime("%B %Y"),
        "recurring_posts": RECURRING_EVENTS["weekly"],
        "monthly_specials": monthly,
        "annual_events": annual_this_month,
        "total_posts": len(RECURRING_EVENTS["weekly"]) * 4 + len(monthly) + len(annual_this_month),
    }
