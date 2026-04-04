"""
Ultron Empire — WebSocket API (V3 Jarvis)
WS /ws/live — Real-time updates for dashboard.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.notifications.websocket import connect, disconnect
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates."""
    await connect(websocket)
    try:
        while True:
            # Keep connection alive, receive any client messages
            data = await websocket.receive_text()
            # Client can send ping/commands
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        disconnect(websocket)
