"""
Ultron Empire — Analyst Conversation Graph (LangGraph)
Main conversation workflow with tool routing and memory.
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
import logging

logger = logging.getLogger(__name__)


class AnalystState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_id: str
    query: str
    memory_context: str
    tools_used: list
    response: str
    needs_deep_analysis: bool


async def retrieve_memory(state: AnalystState) -> dict:
    """Retrieve relevant memories for context."""
    from backend.agents.analyst import _get_memory
    mem = _get_memory()
    context = ""
    if mem:
        try:
            memories = mem.search(state["query"], user_id=state["user_id"], limit=5)
            context = "\n".join(m.get("memory", "") for m in memories if "memory" in m)
        except Exception as e:
            logger.warning(f"Memory retrieval failed: {e}")
    return {"memory_context": context}


async def classify_query(state: AnalystState) -> dict:
    """Classify if query needs simple tool call or deep multi-agent analysis."""
    query_lower = state["query"].lower()
    deep_keywords = [
        "compare", "portfolio restructure", "recommend for client",
        "onboard", "full analysis", "deep dive", "risk assess",
    ]
    needs_deep = any(kw in query_lower for kw in deep_keywords)
    return {"needs_deep_analysis": needs_deep}


def route_analysis(state: AnalystState) -> str:
    """Route to simple or deep analysis."""
    return "deep_analysis" if state.get("needs_deep_analysis") else "simple_analysis"


async def simple_analysis(state: AnalystState) -> dict:
    """Handle simple queries using the standard agent."""
    from backend.agents.analyst import chat_with_ultron
    result = await chat_with_ultron(
        query=state["query"],
        user_id=state["user_id"],
    )
    return {
        "response": result["response"],
        "tools_used": result["tools_used"],
    }


async def deep_analysis(state: AnalystState) -> dict:
    """Handle complex queries using CrewAI multi-agent."""
    from backend.agents.crew import deep_analysis as crew_analyze
    try:
        result = await crew_analyze(state["query"])
        return {"response": str(result), "tools_used": ["crewai_multi_agent"]}
    except Exception as e:
        logger.error(f"Deep analysis failed, falling back: {e}")
        from backend.agents.analyst import chat_with_ultron
        result = await chat_with_ultron(query=state["query"], user_id=state["user_id"])
        return {"response": result["response"], "tools_used": result["tools_used"]}


async def store_memory(state: AnalystState) -> dict:
    """Store the interaction in memory."""
    from backend.agents.analyst import _get_memory
    mem = _get_memory()
    if mem:
        try:
            mem.add(
                f"User asked: {state['query']}\nUltron responded: {state['response'][:500]}",
                user_id=state["user_id"],
            )
        except Exception as e:
            logger.warning(f"Memory storage failed: {e}")
    return {}


def build_analyst_graph():
    graph = StateGraph(AnalystState)

    graph.add_node("retrieve_memory", retrieve_memory)
    graph.add_node("classify_query", classify_query)
    graph.add_node("simple_analysis", simple_analysis)
    graph.add_node("deep_analysis", deep_analysis)
    graph.add_node("store_memory", store_memory)

    graph.set_entry_point("retrieve_memory")
    graph.add_edge("retrieve_memory", "classify_query")
    graph.add_conditional_edges("classify_query", route_analysis, {
        "simple_analysis": "simple_analysis",
        "deep_analysis": "deep_analysis",
    })
    graph.add_edge("simple_analysis", "store_memory")
    graph.add_edge("deep_analysis", "store_memory")
    graph.add_edge("store_memory", END)

    return graph.compile()


analyst_pipeline = build_analyst_graph()
