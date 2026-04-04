"""
Ultron Empire — Voice Pipeline (V3 Jarvis)
Audio in → Whisper STT → Claude Agent → Eleven Labs TTS → Audio out
Target: Under 3 seconds from question to first word of response.
"""

import logging
from io import BytesIO
from backend.voice.transcriber import transcribe_voice
from backend.voice.speaker import text_to_speech
from backend.agents.analyst import chat_with_ultron

logger = logging.getLogger(__name__)


async def voice_chat(audio_path: str) -> dict:
    """Full voice pipeline: Audio → Text → AI → Audio.

    Args:
        audio_path: Path to audio file (WAV/MP3/OGG)

    Returns:
        {"text_input": str, "text_response": str, "audio_response": BytesIO or None}
    """
    # 1. Transcribe with Whisper
    text_input = await transcribe_voice(audio_path)
    if text_input.startswith("Transcription failed") or text_input.startswith("Voice transcription"):
        return {"text_input": "", "text_response": text_input, "audio_response": None}

    logger.info(f"Voice input: {text_input}")

    # 2. Process with Ultron agent
    result = await chat_with_ultron(text_input)
    text_response = result["response"]

    # 3. Convert to speech with Eleven Labs (if configured)
    audio_response = None
    try:
        audio_response = await text_to_speech(text_response[:2000])  # Limit for TTS
        logger.info("Voice response generated")
    except Exception as e:
        logger.warning(f"TTS failed (non-critical): {e}")

    return {
        "text_input": text_input,
        "text_response": text_response,
        "audio_response": audio_response,
        "tools_used": result.get("tools_used", []),
        "response_time_ms": result.get("response_time_ms", 0),
    }
