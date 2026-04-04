"""
Ultron Empire — Celery Beat Schedule
All scheduled tasks. Times in UTC (IST = UTC + 5:30).
"""

from celery.schedules import crontab

# IST 7:30 AM = UTC 2:00 AM
# IST 9:00 AM = UTC 3:30 AM
# IST 9:15 AM = UTC 3:45 AM
# IST 3:30 PM = UTC 10:00 AM
# IST 6:00 PM = UTC 12:30 PM
# IST 9:00 PM = UTC 3:30 PM

beat_schedule = {
    # Market hours (9:15 AM - 3:30 PM IST, Mon-Fri)
    "market-monitor-5min": {
        "task": "workers.market_monitor.check_market",
        "schedule": crontab(minute="*/5", hour="3-10", day_of_week="1-5"),
    },
    # News monitoring (6 AM - 11 PM IST)
    "news-scanner-15min": {
        "task": "workers.news_scanner.scan_news",
        "schedule": crontab(minute="*/15", hour="0-17"),
    },
    # SEBI monitoring (business hours)
    "sebi-checker-hourly": {
        "task": "workers.sebi_checker.check_circulars",
        "schedule": crontab(minute=0, hour="3-12", day_of_week="1-5"),
    },
    # Morning brief (7:30 AM IST)
    "morning-brief": {
        "task": "workers.daily_brief.generate_and_send",
        "schedule": crontab(minute=0, hour=2),
    },
    # Client reminders (9:00 AM IST)
    "client-reminders": {
        "task": "workers.client_reminders.check_reminders",
        "schedule": crontab(minute=30, hour=3),
    },
    # FII/DII update (6:00 PM IST)
    "fii-dii-update": {
        "task": "workers.fii_dii_tracker.update_flows",
        "schedule": crontab(minute=30, hour=12, day_of_week="1-5"),
    },
    # NAV update (9:00 PM IST)
    "nav-update": {
        "task": "workers.nav_tracker.update_navs",
        "schedule": crontab(minute=30, hour=15),
    },
    # Weekly recap (Sunday 8:00 PM IST)
    "weekly-recap": {
        "task": "workers.weekly_recap.generate_and_send",
        "schedule": crontab(minute=30, hour=14, day_of_week=0),
    },
    # Prediction update (9:30 PM IST)
    "prediction-update": {
        "task": "workers.prediction_updater.update_signals",
        "schedule": crontab(minute=0, hour=16),
    },
}

timezone = "UTC"
task_serializer = "json"
accept_content = ["json"]
result_serializer = "json"
task_track_started = True
task_time_limit = 300  # 5 minutes max per task
