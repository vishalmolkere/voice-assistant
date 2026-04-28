"""Natural Language Processing Module using OpenAI GPT."""

import json
import logging
from typing import Any, Dict, List, Optional

import openai

logger = logging.getLogger(__name__)


class NLPProcessor:
    """Convert user input to structured commands using GPT."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.3,
        max_tokens: int = 500,
    ):
        """Initialize NLP processor.

        Args:
            api_key: OpenAI API key
            model: GPT model to use
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        openai.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.conversation_history: List[Dict[str, str]] = []
        logger.info(f"NLPProcessor initialized with {model}")

    def process(
        self, user_input: str, include_context: bool = True
    ) -> Dict[str, Any]:
        """Process user input and extract command.

        Args:
            user_input: User's voice command
            include_context: Include conversation history

        Returns:
            Structured command as JSON
        """
        try:
            logger.info(f"Processing: {user_input}")

            # Build system prompt
            system_prompt = """
            You are a helpful voice assistant. Convert user requests into structured JSON commands.
            Always respond with ONLY valid JSON in this exact format:
            {
                "action": "action_name",
                "parameters": {...},
                "reasoning": "brief explanation"
            }
            
            Supported actions:
            - open_folder: Open a directory
            - create_project: Create a new project
            - write_code: Generate code
            - run_code: Execute a script
            - execute_system: Run system command
            - exit: Close assistant
            
            Only respond with JSON, no other text.
            """

            # Build messages
            messages = [
                {"role": "system", "content": system_prompt},
            ]

            if include_context:
                messages.extend(self.conversation_history)

            messages.append({"role": "user", "content": user_input})

            # Call GPT
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Extract and parse response
            response_text = response["choices"][0]["message"]["content"]
            logger.debug(f"GPT response: {response_text}")

            # Parse JSON
            command = self._parse_json(response_text)
            logger.info(f"Extracted command: {command['action']}")

            # Add to history
            self.conversation_history.append(
                {"role": "user", "content": user_input}
            )
            self.conversation_history.append(
                {"role": "assistant", "content": response_text}
            )

            # Keep history limited
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            return command

        except Exception as e:
            logger.error(f"NLP processing error: {e}")
            return {
                "action": "error",
                "parameters": {"error": str(e)},
                "reasoning": "Processing failed",
            }

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Parse JSON from response text.

        Args:
            text: Response text

        Returns:
            Parsed JSON command
        """
        try:
            # Try to extract JSON from text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error: {e}")

        return {
            "action": "error",
            "parameters": {},
            "reasoning": "Could not parse response",
        }

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history.

        Returns:
            Conversation history
        """
        return self.conversation_history.copy()
