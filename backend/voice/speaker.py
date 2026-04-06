"""
Ultron Empire — Text-to-Speech
Converts Ultron responses to voice using Eleven Labs.
Provides a text-only fallback when the API key is not available.
"""

import logging
from io import BytesIO
from typing import Optional

from backend.config import settings

logger = logging.getLogger(__name__)


async def text_to_speech(
    text: str,
    *,
    allow_text_fallback: bool = True,
) -> Optional[BytesIO]:
    """Convert text to speech using Eleven Labs.

    Args:
        text: Text to convert to speech.
        allow_text_fallback: If True and the API key is missing, return None
            gracefully instead of raising an error.  The caller can then
            fall back to returning the text response without audio.

    Returns:
        BytesIO buffer containing the audio (MP3), or None if the API key
        is not configured and allow_text_fallback is True.
    """
    if not settings.ELEVEN_LABS_API_KEY:
        logger.info(
            "Eleven Labs API key not configured — returning None (text-only mode). "
            "Set ELEVEN_LABS_API_KEY to enable voice responses."
        )
        if allow_text_fallback:
            return None
        raise ValueError(
            "Eleven Labs API key not configured. "
            "Set the ELEVEN_LABS_API_KEY environment variable to enable TTS."
        )

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

    except ImportError:
        logger.error("httpx package is not installed — run `pip install httpx`")
        if allow_text_fallback:
            return None
        raise

    except Exception as e:
        logger.error(f"TTS failed: {e}")
        if allow_text_fallback:
            return None
        raise
