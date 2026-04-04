"""
Ultron Empire — Text-to-Speech
Converts Ultron responses to voice using Eleven Labs.
"""

import logging
from io import BytesIO
from backend.config import settings

logger = logging.getLogger(__name__)


async def text_to_speech(text: str) -> BytesIO:
    """Convert text to speech using Eleven Labs.

    Args:
        text: Text to convert to speech

    Returns:
        BytesIO buffer containing the audio (MP3).
    """
    if not settings.ELEVEN_LABS_API_KEY:
        raise ValueError("Eleven Labs API key not configured")

    try:
        import httpx

        voice_id = settings.ELEVEN_LABS_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"  # Default voice

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": settings.ELEVEN_LABS_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "text": text[:5000],  # Eleven Labs limit
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                },
                timeout=30,
            )
            response.raise_for_status()

        audio_buffer = BytesIO(response.content)
        audio_buffer.seek(0)
        return audio_buffer

    except Exception as e:
        logger.error(f"TTS failed: {e}")
        raise
