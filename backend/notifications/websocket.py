"""Ultron — WebSocket real-time dashboard updates."""

import logging
import json
from datetime import datetime, timezone
from typing import List
from fastapi import WebSocket

logger = logging.getLogger(__name__)

# Connected WebSocket clients
active_connections: List[WebSocket] = []


async def connect(websocket: WebSocket):
    """Accept a new WebSocket connection."""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WebSocket connected. Active: {len(active_connections)}")


def disconnect(websocket: WebSocket):
    """Remove a WebSocket connection."""
    if websocket in active_connections:
        active_connections.remove(websocket)
    logger.info(f"WebSocket disconnected. Active: {len(active_connections)}")


async def broadcast(data: dict):
    """Broadcast data to all connected WebSocket clients."""
    message = json.dumps(data, default=str)
    disconnected = []
    for ws in active_connections:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        disconnect(ws)


def broadcast_alert(priority: str, title: str, message: str, category: str = ""):
    """Broadcast an alert to all dashboard WebSocket clients."""
    import asyncio
    data = {
        "type": "alert",
        "priority": priority,
        "title": title,
        "message": message[:500],
        "category": category,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast(data))
        else:
            asyncio.run(broadcast(data))
    except Exception as e:
        logger.error(f"WebSocket broadcast failed: {e}")


def broadcast_market_update(market_data: dict):
    """Broadcast market data update to dashboards."""
    import asyncio
    data = {"type": "market_update", **market_data}
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast(data))
    except Exception:
        pass
