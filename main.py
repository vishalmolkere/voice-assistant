#!/usr/bin/env python3
"""Voice Assistant Main Application."""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from config.logging_config import LoggerSetup
from modules import (
    CodeGenerator,
    CommandExecutor,
    NLPProcessor,
    SpeechRecognizer,
    TextToSpeech,
    WakeWordDetector,
    ContextMemory,
    SandboxExecutor,
)
from utils.validators import CommandValidator, InputValidator


class VoiceAssistant:
    """Main voice assistant application."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize voice assistant.

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize logger
        logger_config = self.config.get("logging", {})
        self.logger = LoggerSetup.setup(
            log_level=logger_config.get("level", "INFO"),
            log_file=logger_config.get("file", "logs/assistant.log"),
        )
        self.logger.info("=" * 50)
        self.logger.info("Voice Assistant Starting")
        self.logger.info("=" * 50)

        # Initialize modules
        self._initialize_modules()

        # Session state
        self.running = False
        self.session_start = time.time()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file.

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")

            with open(config_file) as f:
                config = yaml.safe_load(f)
            print(f"✓ Configuration loaded from {config_path}")
            return config
        except Exception as e:
            print(f"✗ Failed to load config: {e}")
            sys.exit(1)

    def _initialize_modules(self) -> None:
        """Initialize all modules."""
        try:
            # Get API key from config
            api_key = self.config.get("openai", {}).get("api_key")
            if not api_key or api_key == "your-openai-api-key-here":
                self.logger.error("OpenAI API key not configured")
                raise ValueError("Please configure OpenAI API key in config.yaml")

            # Speech Recognition
            sr_config = self.config.get("speech_recognition", {})
            self.speech_recognizer = SpeechRecognizer(
                model_size=sr_config.get("model_size", "base"),
                language=sr_config.get("language", "en"),
            )
            self.logger.info("✓ Speech Recognizer initialized")

            # NLP Processor
            nlp_config = self.config.get("openai", {})
            self.nlp_processor = NLPProcessor(
                api_key=api_key,
                model=nlp_config.get("model", "gpt-4"),
                temperature=nlp_config.get("temperature", 0.3),
            )
            self.logger.info("✓ NLP Processor initialized")

            # Command Executor
            cmd_config = self.config.get("command_execution", {})
            self.command_executor = CommandExecutor(
                sandbox_mode=cmd_config.get("sandbox_mode", True)
            )
            self.logger.info("✓ Command Executor initialized")

            # Code Generator
            self.code_generator = CodeGenerator(
                api_key=api_key,
                model=nlp_config.get("model", "gpt-4"),
            )
            self.logger.info("✓ Code Generator initialized")

            # Text-to-Speech
            tts_config = self.config.get("text_to_speech", {})
            self.text_to_speech = TextToSpeech(
                rate=tts_config.get("rate", 150),
                volume=tts_config.get("volume", 0.9),
            )
            self.logger.info("✓ Text-to-Speech initialized")

            # Wake Word Detector
            wake_config = self.config.get("wake_word", {})
            self.wake_word_detector = WakeWordDetector(
                wake_word=wake_config.get("phrase", "hey assistant"),
                sensitivity=wake_config.get("sensitivity", 0.5),
            )
            self.logger.info("✓ Wake Word Detector initialized")

            # Context Memory
            session_config = self.config.get("session", {})
            self.context_memory = ContextMemory(
                max_size=session_config.get("context_size", 10),
                persist_file=session_config.get("context_file"),
            )
            self.logger.info("✓ Context Memory initialized")

            # Sandbox Executor
            self.sandbox_executor = SandboxExecutor(
                confirmation_required=cmd_config.get("confirmation_required", True)
            )
            self.logger.info("✓ Sandbox Executor initialized")

            self.logger.info("All modules initialized successfully")

        except Exception as e:
            self.logger.error(f"Module initialization error: {e}")
            raise

    def run(self) -> None:
        """Run the voice assistant main loop."""
        self.running = True
        self.logger.info("Starting listening loop...")
        self.text_to_speech.speak("Voice assistant is ready. Say 'Hey Assistant' to start.")

        try:
            while self.running:
                self._process_loop()
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
            self.text_to_speech.speak("Shutting down. Goodbye!")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self.text_to_speech.speak(f"An error occurred: {str(e)}")
        finally:
            self._shutdown()

    def _process_loop(self) -> None:
        """Single iteration of the processing loop."""
        try:
            # Listen for audio
            print("\n🎤 Listening...")
            user_input = self.speech_recognizer.listen()

            if not InputValidator.validate_text(user_input):
                self.logger.warning("Invalid user input")
                return

            print(f"📝 You said: {user_input}")

            # Check for wake word
            if not self.wake_word_detector.detect(user_input):
                self.logger.debug("Wake word not detected")
                return

            print("✅ Wake word detected!")

            # Process with NLP
            command = self.nlp_processor.process(user_input)

            if not InputValidator.validate_command_dict(command):
                self.logger.error("Invalid command generated")
                self.text_to_speech.speak("I didn't understand that command.")
                return

            # Check sandbox
            action = command.get("action")
            if not self.sandbox_executor.can_execute(action):
                if not self.sandbox_executor.request_confirmation(
                    action, command.get("parameters")
                ):
                    self.logger.warning(f"Command cancelled: {action}")
                    self.text_to_speech.speak("Command cancelled.")
                    return

            # Execute command
            start_time = time.time()
            result = self.command_executor.execute(command)
            duration = time.time() - start_time

            # Log execution
            self.sandbox_executor.log_execution(
                action, result.get("success", False), duration
            )

            # Add to context
            self.context_memory.add(user_input, result, duration)

            # Provide feedback
            if result.get("success"):
                message = result.get("message", "Command executed successfully.")
                print(f"✓ {message}")
                self.text_to_speech.speak(message)
            else:
                error = result.get("error", "Command failed.")
                print(f"✗ {error}")
                self.text_to_speech.speak(f"Error: {error}")

            # Check for exit
            if action == "exit":
                self.running = False

        except Exception as e:
            self.logger.error(f"Processing loop error: {e}")
            self.text_to_speech.speak(f"An error occurred: {str(e)}")

    def _shutdown(self) -> None:
        """Shutdown the assistant."""
        self.running = False
        session_duration = time.time() - self.session_start

        # Print session summary
        summary = self.context_memory.get_summary()
        summary["total_session_duration"] = round(session_duration, 2)
        summary["wake_word_stats"] = self.wake_word_detector.get_detection_stats()

        self.logger.info("=" * 50)
        self.logger.info("Session Summary:")
        for key, value in summary.items():
            self.logger.info(f"  {key}: {value}")
        self.logger.info("=" * 50)
        self.logger.info("Voice Assistant Stopped")


def main() -> None:
    """Main entry point."""
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except Exception as e:
        print(f"✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
