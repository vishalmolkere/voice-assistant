"""Logger utility module."""

import logging
from config.logging_config import LoggerSetup


def get_logger(name: str = "VoiceAssistant") -> logging.Logger:
    """Get configured logger.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    return LoggerSetup.get_logger()
