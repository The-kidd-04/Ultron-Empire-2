"""
Ultron Empire — Chat API
POST /chat — Analyst queries via the AI agent.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional

from backend.agents.analyst import chat_with_ultron
from backend.db.database import SessionLocal
from backend.db.models import ConversationLog

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    user_id: str = "ishaan"
    chat_history: Optional[list] = None


class ChatResponse(BaseModel):
    response: str
    tools_used: list
    response_time_ms: int


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a query to Ultron analyst agent."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = await chat_with_ultron(
        query=request.query,
        user_id=request.user_id,
        chat_history=request.chat_history,
    )

    # Log conversation
    session = SessionLocal()
    try:
        log = ConversationLog(
            user_id=request.user_id,
            channel="dashboard",
            query=request.query,
            response=result["response"][:5000],
            tools_used=result["tools_used"],
            response_time_ms=result["response_time_ms"],
        )
        session.add(log)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

    return ChatResponse(**result)


@router.post("/voice")
async def voice_chat_endpoint(file: UploadFile = File(...)):
    """Send voice audio, get text + audio response."""
    import tempfile, os
    from backend.voice.pipeline import voice_chat

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = await voice_chat(tmp_path)
        return {
            "text_input": result["text_input"],
            "text_response": result["text_response"],
            "has_audio": result.get("audio_response") is not None,
            "tools_used": result.get("tools_used", []),
            "response_time_ms": result.get("response_time_ms", 0),
        }
    finally:
        os.unlink(tmp_path)
