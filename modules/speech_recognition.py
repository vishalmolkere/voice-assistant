"""Speech Recognition Module using OpenAI Whisper."""

import io
import logging
from pathlib import Path
from typing import Optional

import sounddevice as sd
import soundfile as sf
import whisper

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """Real-time speech recognition using Whisper."""

    def __init__(
        self,
        model_size: str = "base",
        language: str = "en",
        sample_rate: int = 16000,
        duration: int = 30,
        device_index: Optional[int] = None,
    ):
        """Initialize speech recognizer.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Language code (en, es, fr, etc.)
            sample_rate: Audio sample rate in Hz
            duration: Maximum recording duration in seconds
            device_index: Audio device index (None = default)
        """
        self.model_size = model_size
        self.language = language
        self.sample_rate = sample_rate
        self.duration = duration
        self.device_index = device_index
        self.model = None
        self._load_model()
        logger.info(f"SpeechRecognizer initialized with {model_size} model")

    def _load_model(self) -> None:
        """Load Whisper model."""
        try:
            logger.info(f"Loading Whisper {self.model_size} model...")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def listen(self, timeout: Optional[float] = None) -> str:
        """Listen to microphone and transcribe audio.

        Args:
            timeout: Maximum listening time in seconds

        Returns:
            Transcribed text
        """
        try:
            logger.info("Listening for audio...")
            # Record audio from microphone
            audio_data = sd.rec(
                int(self.sample_rate * self.duration),
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                device=self.device_index,
                blocking=True,
            )
            logger.debug(f"Recorded audio: {audio_data.shape}")

            # Save to temporary file
            temp_file = Path("/tmp/speech_input.wav")
            sf.write(temp_file, audio_data, self.sample_rate)
            logger.debug(f"Saved temp audio to {temp_file}")

            # Transcribe with Whisper
            result = self.model.transcribe(
                str(temp_file), language=self.language
            )
            text = result["text"].strip()
            logger.info(f"Transcribed: {text}")

            # Cleanup
            temp_file.unlink(missing_ok=True)

            return text

        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            raise

    def transcribe_file(self, file_path: str) -> str:
        """Transcribe audio from file.

        Args:
            file_path: Path to audio file

        Returns:
            Transcribed text
        """
        try:
            logger.info(f"Transcribing file: {file_path}")
            result = self.model.transcribe(
                file_path, language=self.language
            )
            text = result["text"].strip()
            logger.info(f"File transcription complete: {text}")
            return text
        except Exception as e:
            logger.error(f"File transcription error: {e}")
            raise

    def get_available_devices(self) -> list:
        """Get list of available audio devices.

        Returns:
            List of audio device information
        """
        devices = sd.query_devices()
        logger.info(f"Available audio devices: {len(devices)}")
        return devices
