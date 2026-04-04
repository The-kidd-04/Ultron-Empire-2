"""
Ultron Empire — Alert Prioritizer
Ranks and deduplicates alerts to avoid notification fatigue.
"""

import logging
from datetime import datetime, timedelta, timezone
from backend.db.database import SessionLocal
from backend.db.models import Alert

logger = logging.getLogger(__name__)

COOLDOWN_MINUTES = {
    "critical": 5,
    "important": 30,
    "info": 120,
    "client": 60,
}


def should_send_alert(priority: str, category: str, title: str) -> bool:
    """Check if alert should be sent (dedup + cooldown)."""
    session = SessionLocal()
    try:
        cooldown = COOLDOWN_MINUTES.get(priority, 60)
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=cooldown)

        recent = session.query(Alert).filter(
            Alert.priority == priority,
            Alert.category == category,
            Alert.created_at >= cutoff,
        ).first()

        if recent:
            logger.info(f"Alert suppressed (cooldown): [{priority}] {title}")
            return False
        return True
    finally:
        session.close()


def prioritize_alerts(alerts: list) -> list:
    """Sort and filter alerts by priority. Critical first, dedup."""
    priority_order = {"critical": 0, "important": 1, "client": 2, "info": 3}
    sorted_alerts = sorted(alerts, key=lambda a: priority_order.get(a.get("priority", "info"), 3))

    filtered = []
    for alert in sorted_alerts:
        if should_send_alert(alert["priority"], alert["category"], alert.get("title", "")):
            filtered.append(alert)

    return filtered
