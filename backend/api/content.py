"""
Ultron Empire — Content API
POST /content — Generate various content types.
GET  /content/calendar — Get suggested content for today.
"""

from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from backend.agents.content_agent import (
    generate_social_post,
    generate_morning_brief,
    generate_client_message,
    generate_newsletter,
)

router = APIRouter()


class ContentRequest(BaseModel):
    content_type: str  # "social_post", "client_message", "newsletter", "morning_brief", "blog_post", "whatsapp_message"
    topic: Optional[str] = None
    client_name: Optional[str] = None
    context: Optional[str] = None
    tone: Optional[str] = "professional"
    data: Optional[dict] = None


# Content calendar: day-of-week suggestions
CONTENT_CALENDAR = {
    0: {"theme": "Market Outlook", "description": "Start the week with a market outlook post covering key levels, events, and expectations.", "suggested_type": "social_post"},
    1: {"theme": "Fund Spotlight", "description": "Highlight a top-performing PMS or AIF fund with data and analysis.", "suggested_type": "social_post"},
    2: {"theme": "Investor Education", "description": "Educational content — explain a concept like alpha, Sharpe ratio, or PMS vs MF.", "suggested_type": "blog_post"},
    3: {"theme": "Market Mid-Week Review", "description": "Mid-week market review with FII/DII flows, sector rotation, and Nifty analysis.", "suggested_type": "social_post"},
    4: {"theme": "Weekly Recap", "description": "Summarize the week's market action, top PMS performers, and key takeaways.", "suggested_type": "newsletter"},
    5: {"theme": "Weekend Reading", "description": "Curate and recommend insightful reads on investing, markets, or wealth management.", "suggested_type": "blog_post"},
    6: {"theme": "Week Ahead Preview", "description": "Preview the upcoming week — key events, earnings, global cues, and Ultron's positioning.", "suggested_type": "social_post"},
}


@router.post("")
async def generate_content(request: ContentRequest):
    """Generate content based on type."""
    if request.content_type == "social_post":
        result = await generate_social_post(
            topic=request.topic or "Weekly PMS performance update",
            data=request.data,
            format_type="instagram",
        )
    elif request.content_type == "morning_brief":
        result = await generate_morning_brief(
            market_data=request.data.get("market_data") if request.data else None,
            news=request.data.get("news") if request.data else None,
            fii_dii=request.data.get("fii_dii") if request.data else None,
        )
    elif request.content_type == "blog_post":
        result = await generate_social_post(
            topic=request.topic or "PMS investing insights",
            data=request.data,
            format_type="blog",
        )
    elif request.content_type == "whatsapp_message":
        result = await generate_social_post(
            topic=request.topic or "Quick market update",
            data=request.data,
            format_type="whatsapp",
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


@router.get("/calendar")
async def content_calendar():
    """Return suggested content for today based on day of week."""
    today = datetime.now()
    day_of_week = today.weekday()  # 0=Monday, 6=Sunday
    suggestion = CONTENT_CALENDAR[day_of_week]

    return {
        "date": today.strftime("%Y-%m-%d"),
        "day": today.strftime("%A"),
        "theme": suggestion["theme"],
        "description": suggestion["description"],
        "suggested_type": suggestion["suggested_type"],
    }
