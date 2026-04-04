"""
Ultron Analyst Agent — The core intelligence engine.
Built with LangGraph's prebuilt ReAct agent for multi-step reasoning.

This agent:
1. Receives a query from Ishaan (via Telegram or dashboard)
2. Decides which tools to use (fund lookup, market data, news, etc.)
3. Executes tools in the right order
4. Synthesizes a comprehensive response
5. Remembers context from previous conversations (Mem0)
"""

import time
import logging
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from backend.tools.fund_lookup import fund_lookup_tool
from backend.tools.nav_fetcher import nav_fetcher_tool
from backend.tools.news_search import news_search_tool
from backend.tools.market_data import market_data_tool
from backend.tools.sebi_checker import sebi_checker_tool
from backend.tools.client_lookup import client_lookup_tool
from backend.tools.portfolio_analyzer import portfolio_analyzer_tool
from backend.tools.calculator import calculator_tool
from backend.tools.backtester import backtester_tool
from backend.prompts.analyst_system import ANALYST_SYSTEM_PROMPT
from backend.config import settings

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatAnthropic(
    model=settings.CLAUDE_MODEL,
    api_key=settings.ANTHROPIC_API_KEY,
    temperature=0.3,
    max_tokens=4096,
)

# Initialize memory (Mem0)
_memory = None


def _get_memory():
    """Lazy-initialize Mem0 memory."""
    global _memory
    if _memory is None:
        try:
            from mem0 import Memory
            _memory = Memory.from_config({
                "llm": {
                    "provider": "anthropic",
                    "config": {
                        "model": settings.CLAUDE_MODEL,
                        "api_key": settings.ANTHROPIC_API_KEY,
                    },
                },
                "vector_store": {
                    "provider": "chroma",
                    "config": {
                        "collection_name": "ultron_memory",
                        "path": "./data/chroma_db",
                    },
                },
            })
        except Exception as e:
            logger.warning(f"Mem0 initialization failed (non-critical): {e}")
    return _memory


# Register all tools
tools = [
    fund_lookup_tool,
    nav_fetcher_tool,
    news_search_tool,
    market_data_tool,
    sebi_checker_tool,
    client_lookup_tool,
    portfolio_analyzer_tool,
    calculator_tool,
    backtester_tool,
]

# Create the ReAct agent using LangGraph prebuilt
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=ANALYST_SYSTEM_PROMPT,
)


async def chat_with_ultron(
    query: str,
    user_id: str = "ishaan",
    chat_history: Optional[list] = None,
) -> dict:
    """Main entry point for chatting with Ultron.

    Args:
        query: The user's question or request
        user_id: User identifier (for memory)
        chat_history: Previous messages in this conversation

    Returns:
        Dict with 'response' text, 'tools_used' list, and 'response_time_ms'.
    """
    start_time = time.time()
    tools_used = []

    # Retrieve relevant memories
    memory_context = ""
    mem = _get_memory()
    if mem:
        try:
            relevant_memories = mem.search(query, user_id=user_id, limit=5)
            if relevant_memories:
                memory_context = "\n".join(
                    m["memory"] for m in relevant_memories if "memory" in m
                )
        except Exception as e:
            logger.warning(f"Memory retrieval failed: {e}")

    # Enhance the query with memory context
    enhanced_input = query
    if memory_context:
        enhanced_input = (
            f"Context from previous conversations:\n{memory_context}\n\n"
            f"Current query: {query}"
        )

    # Build messages
    messages = []
    if chat_history:
        messages.extend(chat_history)
    messages.append(HumanMessage(content=enhanced_input))

    # Execute the agent
    try:
        result = await agent.ainvoke({"messages": messages})

        # Extract the final AI response
        response_messages = result.get("messages", [])
        response = ""
        for msg in reversed(response_messages):
            if hasattr(msg, "content") and isinstance(msg.content, str) and msg.content.strip():
                response = msg.content
                break

        # Extract tools used from tool call messages
        for msg in response_messages:
            if hasattr(msg, "tool_calls"):
                for tc in msg.tool_calls:
                    tools_used.append(tc.get("name", "unknown"))

        if not response:
            response = "I processed your request but couldn't generate a response. Please try again."

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        response = (
            "I encountered an issue processing your request. "
            "Please try rephrasing or ask a simpler question first. "
            f"Error: {str(e)[:200]}"
        )

    # Store this interaction in memory
    if mem:
        try:
            mem.add(
                f"User asked: {query}\nUltron responded: {response[:500]}",
                user_id=user_id,
            )
        except Exception as e:
            logger.warning(f"Memory storage failed: {e}")

    elapsed_ms = int((time.time() - start_time) * 1000)

    return {
        "response": response,
        "tools_used": list(set(tools_used)),
        "response_time_ms": elapsed_ms,
    }
