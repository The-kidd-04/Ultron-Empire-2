"""
Ultron Empire — Fund Comparison Chain
LangChain chain: Fetch Both Funds → Compare → Recommend.
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.config import settings

llm = ChatAnthropic(model=settings.CLAUDE_MODEL, api_key=settings.ANTHROPIC_API_KEY, temperature=0.3)

comparison_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Ultron. Compare two funds in a clear side-by-side format. Include returns, risk, fees, holdings overlap, and your recommendation. Always consider the client context if provided."),
    ("human", "Fund A Data:\n{fund_a}\n\nFund B Data:\n{fund_b}\n\nClient Context: {client_context}\n\nProvide the comparison."),
])

comparison_chain = comparison_prompt | llm | StrOutputParser()
