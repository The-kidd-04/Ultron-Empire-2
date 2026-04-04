"""
Ultron Empire — Research Graph (LangGraph)
Deep research workflow: gather data → analyze → synthesize → format.
"""

from typing import TypedDict, List
from langgraph.graph import StateGraph, END
import logging

logger = logging.getLogger(__name__)


class ResearchState(TypedDict):
    topic: str
    market_data: str
    news_data: str
    fund_data: str
    analysis: str
    formatted_report: str


async def gather_market_data(state: ResearchState) -> dict:
    from backend.tools.market_data import market_data_tool
    data = market_data_tool.invoke({"indicator": "overview"})
    return {"market_data": data}


async def gather_news(state: ResearchState) -> dict:
    from backend.tools.news_search import news_search_tool
    data = news_search_tool.invoke({"query": state["topic"], "max_results": 5})
    return {"news_data": data}


async def gather_fund_data(state: ResearchState) -> dict:
    from backend.tools.fund_lookup import fund_lookup_tool
    data = fund_lookup_tool.invoke({"query": state["topic"]})
    return {"fund_data": data}


async def analyze_findings(state: ResearchState) -> dict:
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage, SystemMessage
    from backend.config import settings

    llm = ChatAnthropic(model=settings.CLAUDE_MODEL, api_key=settings.ANTHROPIC_API_KEY, temperature=0.3)
    prompt = (
        f"Analyze the following research data on '{state['topic']}':\n\n"
        f"MARKET DATA:\n{state['market_data']}\n\n"
        f"NEWS:\n{state['news_data']}\n\n"
        f"FUND DATA:\n{state['fund_data']}\n\n"
        f"Provide a comprehensive analysis with key findings, implications for PMS/AIF business, "
        f"and actionable insights. Use data points and be specific."
    )
    response = await llm.ainvoke([
        SystemMessage(content="You are Ultron, a senior wealth research analyst for PMS Sahi Hai."),
        HumanMessage(content=prompt),
    ])
    return {"analysis": response.content}


async def format_report(state: ResearchState) -> dict:
    report = (
        f"📊 *Ultron Research Report: {state['topic']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{state['analysis']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"_PMS Sahi Hai | India's 1st AI Powered PMS & AIF Marketplace_"
    )
    return {"formatted_report": report}


def build_research_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("gather_market", gather_market_data)
    graph.add_node("gather_news", gather_news)
    graph.add_node("gather_funds", gather_fund_data)
    graph.add_node("analyze", analyze_findings)
    graph.add_node("format", format_report)

    graph.set_entry_point("gather_market")
    graph.add_edge("gather_market", "gather_news")
    graph.add_edge("gather_news", "gather_funds")
    graph.add_edge("gather_funds", "analyze")
    graph.add_edge("analyze", "format")
    graph.add_edge("format", END)

    return graph.compile()


research_pipeline = build_research_graph()
