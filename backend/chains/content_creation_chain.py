"""
Ultron Empire — Content Creation Chain
LangChain chain: Topic → Research → Draft → Format.
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.config import settings

llm = ChatAnthropic(model=settings.CLAUDE_MODEL, api_key=settings.ANTHROPIC_API_KEY, temperature=0.5)

social_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Ultron's content engine for PMS Sahi Hai. Create engaging social media content (Instagram/LinkedIn). Include data points, hashtags, and a CTA. Brand voice: authoritative yet approachable, AI-forward, premium."),
    ("human", "Content type: {content_type}\nTopic: {topic}\nData: {data}\n\nGenerate the post."),
])

newsletter_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Ultron's content engine for PMS Sahi Hai. Create a professional monthly newsletter for HNI clients. Sections: Market Recap, Fund Highlights, Ultron's Outlook, Tax Tips."),
    ("human", "Market Recap: {market_recap}\nFund Highlights: {fund_highlights}\nOutlook: {outlook}\n\nGenerate the newsletter."),
])

social_content_chain = social_prompt | llm | StrOutputParser()
newsletter_chain = newsletter_prompt | llm | StrOutputParser()
