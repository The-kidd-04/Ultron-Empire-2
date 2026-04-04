"""Ultron Empire — Weekly PMS Performance Recap Generator"""

from backend.agents.analyst import chat_with_ultron


async def generate_weekly_recap() -> str:
    result = await chat_with_ultron(
        "Generate a weekly PMS performance recap. Include top 5 and bottom 5 PMS performers, "
        "Nifty/Sensex weekly change, FII/DII weekly flows, key events, and Ultron's weekly insight. "
        "Format for Instagram/LinkedIn with hashtags."
    )
    return result["response"]
