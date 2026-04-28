"""Input validation utilities."""

import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class InputValidator:
    """Validate user inputs."""

    @staticmethod
    def validate_text(text: str, min_length: int = 1, max_length: int = 1000) -> bool:
        """Validate text input.

        Args:
            text: Text to validate
            min_length: Minimum length
            max_length: Maximum length

        Returns:
            True if valid
        """
        if not isinstance(text, str):
            logger.warning(f"Invalid text type: {type(text)}")
            return False

        if len(text) < min_length or len(text) > max_length:
            logger.warning(f"Text length out of range: {len(text)}")
            return False

        return True

    @staticmethod
    def validate_path(path: str) -> bool:
        """Validate file path.

        Args:
            path: File path to validate

        Returns:
            True if valid
        """
        if not isinstance(path, str) or not path.strip():
            logger.warning(f"Invalid path: {path}")
            return False

        # Check for suspicious patterns
        if ".." in path and not path.startswith(".."):
            logger.warning(f"Suspicious path: {path}")
            return False

        return True

    @staticmethod
    def validate_command_dict(command: Dict[str, Any]) -> bool:
        """Validate command dictionary.

        Args:
            command: Command dictionary

        Returns:
            True if valid
        """
        if not isinstance(command, dict):
            logger.warning(f"Invalid command type: {type(command)}")
            return False

        if "action" not in command:
            logger.warning("Command missing 'action' field")
            return False

        if not isinstance(command.get("parameters"), (dict, type(None))):
            logger.warning("Command 'parameters' must be dict or None")
            return False

        return True


class CommandValidator:
    """Validate command execution."""

    DANGEROUS_PATTERNS = [
        r"rm\s+-rf",  # Recursive delete
        r":\(\w\+d,/\)",  # Bash fork bomb
        r"(?i)format",  # Format command
    ]

    @staticmethod
    def is_safe_command(command: str) -> bool:
        """Check if command is safe to execute.

        Args:
            command: Command string

        Returns:
            True if safe
        """
        for pattern in CommandValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, command):
                logger.warning(f"Dangerous command pattern detected: {pattern}")
                return False

        return True

    @staticmethod
    def validate_file_operation(
        operation: str, path: str
    ) -> bool:
        """Validate file operation.

        Args:
            operation: Operation type (read, write, delete)
            path: File path

        Returns:
            True if valid
        """
        if operation not in ["read", "write", "delete"]:
            logger.warning(f"Invalid operation: {operation}")
            return False

        if not InputValidator.validate_path(path):
            return False

        if operation == "delete" and path in ["/", "/root", "/home"]:
            logger.warning(f"Refusing to delete system path: {path}")
            return False

        return True
