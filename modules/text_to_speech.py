"""Text-to-Speech Module using pyttsx3."""

import logging
from pathlib import Path
from typing import Optional

import pyttsx3

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Convert text to speech using pyttsx3."""

    def __init__(
        self,
        rate: int = 150,
        volume: float = 0.9,
        voice_index: int = 0,
    ):
        """Initialize text-to-speech engine.

        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            voice_index: Voice index (varies by system)
        """
        self.engine = pyttsx3.init()
        self.rate = rate
        self.volume = volume
        self.voice_index = voice_index
        self._configure_engine()
        logger.info("TextToSpeech initialized")

    def _configure_engine(self) -> None:
        """Configure pyttsx3 engine."""
        self.engine.setProperty("rate", self.rate)
        self.engine.setProperty("volume", self.volume)

        voices = self.engine.getProperty("voices")
        if 0 <= self.voice_index < len(voices):
            self.engine.setProperty("voice", voices[self.voice_index].id)
        logger.debug(f"TTS configured: rate={self.rate}, volume={self.volume}")

    def speak(self, text: str) -> None:
        """Speak text using TTS.

        Args:
            text: Text to speak
        """
        try:
            if not text or not isinstance(text, str):
                logger.warning(f"Invalid text input: {text}")
                return

            logger.info(f"Speaking: {text[:50]}...")
            self.engine.say(text)
            self.engine.runAndWait()
            logger.debug("Speech completed")

        except Exception as e:
            logger.error(f"TTS error: {e}")

    def speak_async(self, text: str) -> None:
        """Speak text asynchronously.

        Args:
            text: Text to speak
        """
        try:
            if not text or not isinstance(text, str):
                logger.warning(f"Invalid text input: {text}")
                return

            logger.info(f"Speaking (async): {text[:50]}...")
            self.engine.say(text)
            # Don't wait for completion
            logger.debug("Async speech queued")

        except Exception as e:
            logger.error(f"Async TTS error: {e}")

    def save_to_file(
        self, text: str, filename: str
    ) -> Optional[Path]:
        """Save speech to audio file.

        Args:
            text: Text to speak
            filename: Output filename

        Returns:
            Path to saved file or None
        """
        try:
            file_path = Path(filename)
            logger.info(f"Saving speech to {file_path}")

            self.engine.save_to_file(text, str(file_path))
            self.engine.runAndWait()

            logger.info(f"Speech saved to {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Save to file error: {e}")
            return None

    def get_voices(self) -> list:
        """Get available voices.

        Returns:
            List of available voices
        """
        voices = self.engine.getProperty("voices")
        logger.info(f"Available voices: {len(voices)}")
        return [voice.name for voice in voices]

    def set_voice(self, voice_index: int) -> None:
        """Set voice by index.

        Args:
            voice_index: Voice index
        """
        voices = self.engine.getProperty("voices")
        if 0 <= voice_index < len(voices):
            self.engine.setProperty("voice", voices[voice_index].id)
            self.voice_index = voice_index
            logger.info(f"Voice changed to index {voice_index}")
        else:
            logger.warning(f"Invalid voice index: {voice_index}")

    def set_rate(self, rate: int) -> None:
        """Set speech rate.

        Args:
            rate: Speech rate (words per minute)
        """
        self.rate = rate
        self.engine.setProperty("rate", rate)
        logger.info(f"Rate changed to {rate}")

    def set_volume(self, volume: float) -> None:
        """Set volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        self.engine.setProperty("volume", self.volume)
        logger.info(f"Volume changed to {self.volume}")
