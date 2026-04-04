"""
Ultron Empire — Alert Engine
Central alert processing, storage, and routing.
"""

import logging
from datetime import datetime, timezone
from backend.db.database import SessionLocal
from backend.db.models import Alert

logger = logging.getLogger(__name__)


def store_alert(
    priority: str,
    category: str,
    title: str,
    message: str,
    event_data: dict = None,
    client_id: int = None,
    delivered_via: list = None,
) -> Alert:
    """Store an alert in the database."""
    session = SessionLocal()
    try:
        alert = Alert(
            priority=priority,
            category=category,
            title=title,
            message=message,
            event_data=event_data or {},
            client_id=client_id,
            delivered_via=delivered_via or [],
        )
        session.add(alert)
        session.commit()
        session.refresh(alert)
        logger.info(f"Alert stored: [{priority}] {title}")
        return alert
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to store alert: {e}")
        raise
    finally:
        session.close()


def get_recent_alerts(limit: int = 20, priority: str = None) -> list:
    """Get recent alerts, optionally filtered by priority."""
    session = SessionLocal()
    try:
        q = session.query(Alert).order_by(Alert.created_at.desc())
        if priority:
            q = q.filter(Alert.priority == priority)
        return q.limit(limit).all()
    finally:
        session.close()


def mark_alert_read(alert_id: int) -> bool:
    """Mark an alert as read."""
    session = SessionLocal()
    try:
        alert = session.query(Alert).get(alert_id)
        if alert:
            alert.is_read = True
            session.commit()
            return True
        return False
    finally:
        session.close()
