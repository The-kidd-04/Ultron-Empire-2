"""
Ultron Empire — Voice Transcription
Transcribes voice notes using Google Speech Recognition (free, no API key)
with OpenAI Whisper as optional upgrade.
"""

import logging
import os
from backend.config import settings

logger = logging.getLogger(__name__)


async def transcribe_voice(audio_path: str) -> str:
    """Transcribe a voice message to text.

    Uses Google Speech Recognition (free, no API key needed) by default.
    If OPENAI_API_KEY is set, uses OpenAI Whisper for better accuracy.

    Args:
        audio_path: Path to audio file (OGG, MP3, WAV, M4A)

    Returns:
        Transcribed text, or an error message if transcription fails.
    """
    # If OpenAI key is available, use Whisper (better accuracy)
    if settings.OPENAI_API_KEY:
        return await _transcribe_whisper(audio_path)

    # Otherwise use free Google Speech Recognition
    return await _transcribe_google_free(audio_path)


async def _transcribe_google_free(audio_path: str) -> str:
    """Transcribe using Google's free Speech Recognition API (no key needed)."""
    try:
        import speech_recognition as sr
        from pydub import AudioSegment

        # Convert to WAV (speech_recognition needs WAV)
        wav_path = audio_path.rsplit(".", 1)[0] + "_converted.wav"
        try:
            audio = AudioSegment.from_file(audio_path)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(wav_path, format="wav")
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            return f"Could not convert audio file: {e}"

        # Transcribe
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data, language="en-IN")
        except sr.UnknownValueError:
            text = ""
        except sr.RequestError as e:
            logger.error(f"Google Speech API error: {e}")
            return f"Speech recognition service error: {e}"

        # Cleanup temp file
        try:
            os.remove(wav_path)
        except OSError:
            pass

        if not text:
            return "Could not understand the audio. Please try speaking more clearly."

        return text.strip()

    except ImportError as e:
        logger.error(f"Missing package for voice transcription: {e}")
        return (
            "Voice transcription requires 'SpeechRecognition' and 'pydub' packages. "
            "Install with: pip install SpeechRecognition pydub"
        )
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return f"Transcription failed: {str(e)}"


async def _transcribe_whisper(audio_path: str) -> str:
    """Transcribe using OpenAI Whisper API (requires OPENAI_API_KEY)."""
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

    except ImportError:
        logger.warning("openai package not installed, falling back to Google Speech")
        return await _transcribe_google_free(audio_path)

    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        # Fall back to Google free
        logger.info("Falling back to Google Speech Recognition")
        return await _transcribe_google_free(audio_path)
