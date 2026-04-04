"""
Ultron Empire — Client Report Chain
LangChain chain: Fetch Portfolio → Analyze → Generate Report.
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.config import settings

llm = ChatAnthropic(model=settings.CLAUDE_MODEL, api_key=settings.ANTHROPIC_API_KEY, temperature=0.3)

report_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Ultron. Generate a comprehensive client portfolio report for PMS Sahi Hai. Include portfolio summary, performance, risk, and recommendations. Use ₹, Cr/L format."),
    ("human", "Client: {client_name}\nProfile: {client_profile}\nHoldings: {holdings}\nGoals: {goals}\n\nGenerate the report."),
])

client_report_chain = report_prompt | llm | StrOutputParser()
