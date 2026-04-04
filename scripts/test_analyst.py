"""Test Ultron analyst agent with sample queries."""

import asyncio
from backend.agents.analyst import chat_with_ultron

SAMPLE_QUERIES = [
    "Compare Quant Small Cap PMS vs Stallion Asset Core PMS",
    "What's the current market snapshot?",
    "Tell me about client Rajesh Mehta",
    "Which PMS has the best Sharpe ratio?",
    "Calculate CAGR if ₹1 Cr becomes ₹3 Cr in 5 years",
]


async def main():
    for q in SAMPLE_QUERIES:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        result = await chat_with_ultron(q)
        print(f"A: {result['response'][:300]}...")
        print(f"Tools: {result['tools_used']} | Time: {result['response_time_ms']}ms")


if __name__ == "__main__":
    asyncio.run(main())
