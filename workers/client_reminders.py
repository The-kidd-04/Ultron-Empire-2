"""
Ultron Empire — Client Reminders Worker
Checks for upcoming reviews, renewals, and anniversaries at 9 AM IST.
"""

import asyncio
import logging
from datetime import date, timedelta
from workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(name="workers.client_reminders.check_reminders")
def check_reminders():
    """Check for client review and renewal reminders."""
    asyncio.run(_check_reminders_async())


async def _check_reminders_async():
    from backend.db.database import SessionLocal
    from backend.db.models import Client
    from backend.alerts.telegram_bot import send_alert_to_telegram
    from backend.alerts.engine import store_alert

    session = SessionLocal()
    try:
        today = date.today()
        upcoming = today + timedelta(days=7)

        # Reviews due in next 7 days
        clients = session.query(Client).filter(
            Client.next_review_date.between(today, upcoming)
        ).all()

        if clients:
            lines = []
            for c in clients:
                days_until = (c.next_review_date - today).days
                lines.append(
                    f"  • {c.name} — review on {c.next_review_date} "
                    f"({'TODAY' if days_until == 0 else f'in {days_until} days'})"
                )

            message = (
                f"📅 *Client Review Reminders*\n\n"
                f"{chr(10).join(lines)}\n\n"
                f"Use /client `<name>` for a pre-meeting brief."
            )
            await send_alert_to_telegram(message, "client")

            for c in clients:
                store_alert(
                    priority="client",
                    category="review_reminder",
                    title=f"Review due: {c.name}",
                    message=f"Client review scheduled for {c.next_review_date}",
                    client_id=c.id,
                    delivered_via=["telegram"],
                )

        logger.info(f"Reminder check: {len(clients)} upcoming reviews")
    except Exception as e:
        logger.error(f"Reminder check failed: {e}")
    finally:
        session.close()
