"""
Ultron Empire — Alert Processing Chain
LangChain chain: Event → Classify → Generate Message.
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.config import settings

llm = ChatAnthropic(model=settings.CLAUDE_MODEL, api_key=settings.ANTHROPIC_API_KEY, temperature=0.2)

classify_prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify this financial event as: critical, important, info, or client. Respond with one word only."),
    ("human", "Event: {event_type}\nDetails: {event_details}"),
])

alert_prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate a concise Telegram alert for PMS Sahi Hai. Use appropriate emoji (🔴 critical, 🟡 important, 🔵 info). Keep under 500 chars. Include headline, what happened, and recommendation."),
    ("human", "Severity: {severity}\nEvent: {event_details}\nAffected: {affected}"),
])

classify_chain = classify_prompt | llm | StrOutputParser()
alert_message_chain = alert_prompt | llm | StrOutputParser()
