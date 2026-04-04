"""
Ultron Empire — Voice Transcription
Transcribes voice notes using OpenAI Whisper.
"""

import logging
from backend.config import settings

logger = logging.getLogger(__name__)


async def transcribe_voice(audio_path: str) -> str:
    """Transcribe a voice message to text using Whisper.

    Args:
        audio_path: Path to audio file (OGG, MP3, WAV, M4A)

    Returns:
        Transcribed text.
    """
    if not settings.OPENAI_API_KEY:
        return "Voice transcription requires OpenAI API key for Whisper."

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",
                response_format="text",
            )

        return transcript.strip()

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return f"Transcription failed: {str(e)}"
