"""
Ultron Empire — Alerts API
GET/POST /alerts — Alert management.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

from backend.alerts.engine import get_recent_alerts, store_alert, mark_alert_read

router = APIRouter()


class AlertResponse(BaseModel):
    id: int
    priority: str
    category: Optional[str]
    title: Optional[str]
    message: Optional[str]
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True


@router.get("")
async def list_alerts(
    limit: int = Query(default=20, le=100),
    priority: Optional[str] = None,
):
    """Get recent alerts."""
    alerts = get_recent_alerts(limit=limit, priority=priority)
    return [
        {
            "id": a.id,
            "priority": a.priority,
            "category": a.category,
            "title": a.title,
            "message": a.message,
            "is_read": a.is_read,
            "delivered_via": a.delivered_via,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]


class AlertCreateRequest(BaseModel):
    priority: str
    category: str
    title: str
    message: str
    event_data: Optional[dict] = None
    client_id: Optional[int] = None


@router.post("")
async def create_alert(request: AlertCreateRequest):
    """Create a new alert."""
    alert = store_alert(
        priority=request.priority,
        category=request.category,
        title=request.title,
        message=request.message,
        event_data=request.event_data,
        client_id=request.client_id,
    )
    return {"id": alert.id, "status": "created"}


@router.patch("/{alert_id}/read")
async def read_alert(alert_id: int):
    """Mark an alert as read."""
    success = mark_alert_read(alert_id)
    if not success:
        return {"error": "Alert not found"}
    return {"status": "marked_read"}
