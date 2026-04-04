"""
Ultron Empire — CrewAI Multi-Agent Setup
Specialized agents collaborate on complex analysis queries.

Agents:
1. Research Analyst — Finds and analyzes fund/market data
2. Risk Assessor — Evaluates risk implications
3. Client Advisor — Considers client-specific factors
4. Compliance Officer — Checks SEBI regulations and disclaimers
"""

import logging
from crewai import Agent, Task, Crew, Process
from langchain_anthropic import ChatAnthropic
from backend.config import settings

logger = logging.getLogger(__name__)

llm = ChatAnthropic(
    model=settings.CLAUDE_MODEL,
    api_key=settings.ANTHROPIC_API_KEY,
    temperature=0.3,
)

research_analyst = Agent(
    role="Senior Research Analyst",
    goal="Provide deep, data-driven analysis of PMS, AIF, and mutual fund strategies",
    backstory=(
        "You are a CFA charterholder with 15 years of experience analyzing Indian equity markets. "
        "You specialize in PMS and AIF analysis. You always back your views with data and historical patterns."
    ),
    llm=llm,
    verbose=True,
)

risk_assessor = Agent(
    role="Risk Assessment Specialist",
    goal="Evaluate portfolio risks, drawdown potential, and concentration risks",
    backstory=(
        "You are a risk management expert who has worked at top institutional investors. "
        "You think in terms of worst-case scenarios, correlation risks, and tail events. "
        "You never let optimism override prudent risk management."
    ),
    llm=llm,
    verbose=True,
)

client_advisor = Agent(
    role="Client Relationship Advisor",
    goal="Tailor recommendations to specific client profiles and needs",
    backstory=(
        "You understand HNI client psychology deeply. A 55-year-old conservative investor "
        "needs different advice than a 35-year-old aggressive one. You always consider tax "
        "implications, liquidity needs, and emotional factors."
    ),
    llm=llm,
    verbose=True,
)

compliance_officer = Agent(
    role="Compliance Officer",
    goal="Ensure all recommendations comply with SEBI regulations",
    backstory=(
        "You are a SEBI compliance expert. You check every recommendation against current "
        "regulations, ensure proper risk disclosures, and flag compliance issues. "
        "You know PMS, AIF, and MF regulations thoroughly."
    ),
    llm=llm,
    verbose=True,
)


async def deep_analysis(query: str, client_context: dict = None) -> str:
    """Run full multi-agent analysis for complex queries.

    Use for:
    - Complex fund comparisons with client-specific context
    - Portfolio restructuring recommendations
    - New client onboarding recommendations
    - Significant market event analysis
    """
    research_task = Task(
        description=f"Research and analyze: {query}. Provide data-driven findings with specific numbers.",
        agent=research_analyst,
        expected_output="Detailed analysis with data points, comparisons, and trends",
    )

    risk_task = Task(
        description=f"Assess all risk factors for: {query}. Include worst-case scenarios and drawdown potential.",
        agent=risk_assessor,
        expected_output="Risk assessment with drawdown analysis and mitigation strategies",
    )

    client_task = Task(
        description=(
            f"Given the research and risk analysis, provide tailored advice. "
            f"Client context: {client_context or 'General HNI investor'}"
        ),
        agent=client_advisor,
        expected_output="Client-specific recommendation with clear action items",
    )

    compliance_task = Task(
        description="Review the final recommendation for SEBI compliance and add appropriate disclaimers.",
        agent=compliance_officer,
        expected_output="Compliance-checked recommendation with proper disclosures",
    )

    crew = Crew(
        agents=[research_analyst, risk_assessor, client_advisor, compliance_officer],
        tasks=[research_task, risk_task, client_task, compliance_task],
        process=Process.sequential,
        verbose=True,
    )

    try:
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        logger.error(f"CrewAI analysis failed: {e}")
        return f"Multi-agent analysis encountered an error: {str(e)}"
