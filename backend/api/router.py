"""
Ultron Empire — API Router
Mounts all API route modules.
"""

from fastapi import APIRouter

from backend.api.chat import router as chat_router
from backend.api.alerts import router as alerts_router
from backend.api.clients import router as clients_router
from backend.api.market import router as market_router
from backend.api.content import router as content_router
from backend.api.reports import router as reports_router
from backend.api.documents import router as documents_router
from backend.api.predictions import router as predictions_router
from backend.api.webhooks import router as webhooks_router
from backend.api.analytics import router as analytics_router
from backend.api.dashboard import router as dashboard_router
from backend.api.ws import router as ws_router

api_router = APIRouter()

api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(clients_router, prefix="/clients", tags=["Clients"])
api_router.include_router(market_router, prefix="/market", tags=["Market"])
api_router.include_router(content_router, prefix="/content", tags=["Content"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(predictions_router, prefix="/predictions", tags=["Predictions"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(ws_router, prefix="/ws", tags=["WebSocket"])
