"""Voice Assistant Modules."""

from modules.speech_recognition import SpeechRecognizer
from modules.nlp_processor import NLPProcessor
from modules.command_executor import CommandExecutor
from modules.code_generator import CodeGenerator
from modules.text_to_speech import TextToSpeech
from modules.advanced_features import (
    WakeWordDetector,
    ContextMemory,
    SandboxExecutor,
)

__all__ = [
    "SpeechRecognizer",
    "NLPProcessor",
    "CommandExecutor",
    "CodeGenerator",
    "TextToSpeech",
    "WakeWordDetector",
    "ContextMemory",
    "SandboxExecutor",
]
