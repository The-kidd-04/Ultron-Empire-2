"""
Ultron Empire — Vapi Voice Agent Webhook
Handles tool calls from Vapi's conversational AI.
Vapi sends tool calls in its own format, this translates them to our internal APIs.
"""

import logging
from fastapi import APIRouter, Request
from backend.agents.analyst import chat_with_ultron

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ask_ultron")
async def vapi_ask_ultron(request: Request):
    """Handle ask_ultron tool calls from Vapi."""
    body = await request.json()
    logger.info(f"Vapi ask_ultron call received")

    try:
        # Extract the query from Vapi's format
        query = _extract_arg(body, "query")
        if not query:
            return _vapi_response(body, "No query provided. Please ask a question.")

        result = await chat_with_ultron(query)
        return _vapi_response(body, result["response"])

    except Exception as e:
        logger.error(f"Vapi ask_ultron error: {e}")
        return _vapi_response(body, f"Error processing request: {str(e)[:200]}")


@router.post("/get_market_data")
async def vapi_get_market(request: Request):
    """Handle get_market_data tool calls from Vapi."""
    body = await request.json()
    logger.info(f"Vapi get_market_data call received")

    try:
        from backend.tools.market_data import market_data_tool
        result = market_data_tool.invoke({"indicator": "overview"})
        return _vapi_response(body, result)

    except Exception as e:
        logger.error(f"Vapi market data error: {e}")
        return _vapi_response(body, f"Error fetching market data: {str(e)[:200]}")


@router.post("/deliver_analysis")
async def vapi_deliver(request: Request):
    """Handle deliver_analysis tool calls from Vapi."""
    body = await request.json()
    logger.info(f"Vapi deliver_analysis call received")

    try:
        subject = _extract_arg(body, "subject")
        analysis_type = _extract_arg(body, "analysis_type") or "full"
        compare_with = _extract_arg(body, "compare_with")

        if not subject:
            return _vapi_response(body, "Please specify what to analyze.")

        # Import and trigger delivery in background
        from backend.api.deliver import _generate_and_send
        import asyncio
        asyncio.create_task(_generate_and_send(subject, analysis_type, "telegram", compare_with))

        return _vapi_response(
            body,
            f"Got it. I'm generating a full analysis of {subject} and sending it to your Telegram. "
            f"You'll receive it in about 30 seconds."
        )

    except Exception as e:
        logger.error(f"Vapi deliver error: {e}")
        return _vapi_response(body, f"Error: {str(e)[:200]}")


def _extract_arg(body: dict, arg_name: str) -> str:
    """Extract a tool call argument from Vapi's request format."""
    # Try Vapi's standard format
    message = body.get("message", {})
    tool_calls = message.get("toolCallList", [])
    for tc in tool_calls:
        args = tc.get("arguments", {})
        if arg_name in args:
            return args[arg_name]

    # Try toolWithToolCallList format
    for tc in message.get("toolWithToolCallList", []):
        tool_call = tc.get("toolCall", {})
        args = tool_call.get("arguments", {})
        if arg_name in args:
            return args[arg_name]

    # Try direct body (fallback)
    if arg_name in body:
        return body[arg_name]

    return None


def _extract_tool_call_id(body: dict) -> str:
    """Extract the tool call ID from Vapi's request."""
    message = body.get("message", {})
    tool_calls = message.get("toolCallList", [])
    if tool_calls:
        return tool_calls[0].get("id", "")

    for tc in message.get("toolWithToolCallList", []):
        tool_call = tc.get("toolCall", {})
        if tool_call.get("id"):
            return tool_call["id"]

    return ""


def _vapi_response(body: dict, result: str) -> dict:
    """Format response in Vapi's expected format."""
    tool_call_id = _extract_tool_call_id(body)
    return {
        "results": [
            {
                "toolCallId": tool_call_id,
                "result": result,
            }
        ]
    }
