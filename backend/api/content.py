"""
Ultron Empire — Content API
POST /content — Generate various content types.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from backend.agents.content_agent import (
    generate_social_post,
    generate_client_message,
    generate_newsletter,
)

router = APIRouter()


class ContentRequest(BaseModel):
    content_type: str  # "social_post", "client_message", "newsletter"
    topic: Optional[str] = None
    client_name: Optional[str] = None
    context: Optional[str] = None
    tone: Optional[str] = "professional"
    data: Optional[dict] = None


@router.post("")
async def generate_content(request: ContentRequest):
    """Generate content based on type."""
    if request.content_type == "social_post":
        result = await generate_social_post(
            topic=request.topic or "Weekly PMS performance update",
            data=request.data,
        )
    elif request.content_type == "client_message":
        if not request.client_name or not request.context:
            return {"error": "client_name and context required for client messages"}
        result = await generate_client_message(
            client_name=request.client_name,
            context=request.context,
            tone=request.tone or "professional",
        )
    elif request.content_type == "newsletter":
        result = await generate_newsletter(
            market_recap=request.data.get("market_recap", "") if request.data else "",
            fund_highlights=request.data.get("fund_highlights", "") if request.data else "",
            outlook=request.data.get("outlook", "") if request.data else "",
        )
    else:
        return {"error": f"Unknown content type: {request.content_type}"}

    return {"content": result, "content_type": request.content_type}
