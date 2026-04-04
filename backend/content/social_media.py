"""Ultron Empire — Social Media Content Generator"""

from backend.agents.content_agent import generate_social_post


async def create_instagram_post(topic: str, data: dict = None) -> str:
    return await generate_social_post(topic=topic, data=data)


async def create_linkedin_post(topic: str, data: dict = None) -> str:
    return await generate_social_post(topic=f"[LinkedIn] {topic}", data=data)
