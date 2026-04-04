"""
Ultron Empire — Morning Brief Chain
LangChain chain: Gather Data → Analyze → Format → Deliver.
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.config import settings

llm = ChatAnthropic(model=settings.CLAUDE_MODEL, api_key=settings.ANTHROPIC_API_KEY, temperature=0.4)

brief_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Ultron, the AI analyst for PMS Sahi Hai. Generate a morning market brief for Telegram. Use emojis, bold headings, and clean formatting."),
    ("human", "Market Data:\n{market_data}\n\nNews:\n{news}\n\nFII/DII:\n{fii_dii}\n\nGenerate the morning brief."),
])

morning_brief_chain = brief_prompt | llm | StrOutputParser()
