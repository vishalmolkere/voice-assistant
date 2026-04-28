"""Advanced Features: Wake Word Detection, Context Memory, Sandbox Mode."""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Detect wake word in speech."""

    def __init__(
        self,
        wake_word: str = "hey assistant",
        sensitivity: float = 0.5,
        fuzzy_threshold: float = 0.8,
    ):
        """Initialize wake word detector.

        Args:
            wake_word: Wake word phrase
            sensitivity: Detection sensitivity (0.0-1.0)
            fuzzy_threshold: Fuzzy match threshold
        """
        self.wake_word = wake_word.lower()
        self.sensitivity = max(0.0, min(1.0, sensitivity))
        self.fuzzy_threshold = fuzzy_threshold
        self.detection_stats = {
            "total_detections": 0,
            "exact_matches": 0,
            "fuzzy_matches": 0,
            "last_detection": None,
        }
        logger.info(
            f"WakeWordDetector initialized: '{self.wake_word}' (sensitivity: {self.sensitivity})"
        )

    def detect(self, text: str) -> bool:
        """Detect wake word in text.

        Args:
            text: Text to search

        Returns:
            True if wake word detected
        """
        text_lower = text.lower()

        # Exact match
        if self.wake_word in text_lower:
            self.detection_stats["exact_matches"] += 1
            self.detection_stats["total_detections"] += 1
            self.detection_stats["last_detection"] = datetime.now().isoformat()
            logger.info(f"Wake word detected (exact): {self.wake_word}")
            return True

        # Fuzzy match
        if self._fuzzy_match(text_lower):
            self.detection_stats["fuzzy_matches"] += 1
            self.detection_stats["total_detections"] += 1
            self.detection_stats["last_detection"] = datetime.now().isoformat()
            logger.info(f"Wake word detected (fuzzy): {self.wake_word}")
            return True

        return False

    def _fuzzy_match(self, text: str) -> bool:
        """Perform fuzzy matching.

        Args:
            text: Text to search

        Returns:
            True if fuzzy match found
        """
        words = text.split()
        wake_words = self.wake_word.split()

        for i in range(len(words) - len(wake_words) + 1):
            match_score = sum(
                1
                for j, wake_word in enumerate(wake_words)
                if self._string_similarity(words[i + j], wake_word)
                > self.fuzzy_threshold
            )
            if match_score == len(wake_words):
                return self.sensitivity > 0.3

        return False

    @staticmethod
    def _string_similarity(s1: str, s2: str) -> float:
        """Calculate string similarity.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score (0.0-1.0)
        """
        from difflib import SequenceMatcher

        return SequenceMatcher(None, s1, s2).ratio()

    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection statistics.

        Returns:
            Detection statistics
        """
        return self.detection_stats.copy()

    def reset_stats(self) -> None:
        """Reset detection statistics."""
        self.detection_stats = {
            "total_detections": 0,
            "exact_matches": 0,
            "fuzzy_matches": 0,
            "last_detection": None,
        }
        logger.info("Detection stats reset")


class ContextMemory:
    """Maintain context and command history."""

    def __init__(
        self,
        max_size: int = 10,
        persist_file: Optional[str] = None,
    ):
        """Initialize context memory.

        Args:
            max_size: Maximum number of commands to remember
            persist_file: Optional file to persist history
        """
        self.max_size = max_size
        self.persist_file = Path(persist_file) if persist_file else None
        self.history: List[Dict[str, Any]] = []
        self._load_history()
        logger.info(f"ContextMemory initialized (max_size: {max_size})")

    def add(
        self,
        command: str,
        result: Any,
        duration: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add command to history.

        Args:
            command: Command text
            result: Command result
            duration: Execution duration in seconds
            metadata: Additional metadata
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "result": result,
            "duration": duration,
            "metadata": metadata or {},
        }

        self.history.append(entry)

        # Keep history limited
        if len(self.history) > self.max_size:
            self.history = self.history[-self.max_size :]

        # Persist if configured
        if self.persist_file:
            self._save_history()

        logger.debug(f"Command added to history: {command[:50]}...")

    def get_recent(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent commands.

        Args:
            count: Number of recent commands

        Returns:
            List of recent commands
        """
        return self.history[-count:]

    def search(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search command history.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Matching commands
        """
        query_lower = query.lower()
        results = [
            entry
            for entry in self.history
            if query_lower in entry["command"].lower()
        ]
        logger.info(f"History search: '{query}' found {len(results)} matches")
        return results[:limit]

    def get_summary(self) -> Dict[str, Any]:
        """Get session summary.

        Returns:
            Session summary
        """
        if not self.history:
            return {"total_commands": 0, "total_duration": 0.0}

        total_duration = sum(entry["duration"] for entry in self.history)
        avg_duration = total_duration / len(self.history) if self.history else 0

        summary = {
            "total_commands": len(self.history),
            "total_duration": round(total_duration, 2),
            "average_duration": round(avg_duration, 2),
            "first_command": self.history[0]["timestamp"],
            "last_command": self.history[-1]["timestamp"],
        }

        logger.info(f"Session summary: {summary}")
        return summary

    def _save_history(self) -> None:
        """Save history to file."""
        try:
            if self.persist_file:
                self.persist_file.parent.mkdir(parents=True, exist_ok=True)
                self.persist_file.write_text(
                    json.dumps(self.history, indent=2)
                )
                logger.debug(f"History saved to {self.persist_file}")
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def _load_history(self) -> None:
        """Load history from file."""
        try:
            if self.persist_file and self.persist_file.exists():
                self.history = json.loads(self.persist_file.read_text())
                logger.info(
                    f"Loaded {len(self.history)} commands from history file"
                )
        except Exception as e:
            logger.error(f"Failed to load history: {e}")

    def clear(self) -> None:
        """Clear history."""
        self.history.clear()
        if self.persist_file:
            self._save_history()
        logger.info("History cleared")


class SandboxExecutor:
    """Execute commands safely with sandbox restrictions."""

    RISKY_ACTIONS = {
        "execute_system",
        "delete_file",
        "modify_system",
        "install_package",
    }

    SAFE_ACTIONS = {
        "open_folder",
        "create_project",
        "write_code",
        "run_code",
    }

    def __init__(
        self,
        confirmation_required: bool = True,
        max_execution_time: int = 30,
    ):
        """Initialize sandbox executor.

        Args:
            confirmation_required: Require user confirmation for risky actions
            max_execution_time: Maximum execution time in seconds
        """
        self.confirmation_required = confirmation_required
        self.max_execution_time = max_execution_time
        self.execution_log: List[Dict[str, Any]] = []
        logger.info(
            f"SandboxExecutor initialized (confirmation: {confirmation_required})"
        )

    def can_execute(
        self, action: str, parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check if action can be executed.

        Args:
            action: Action name
            parameters: Action parameters

        Returns:
            True if action is allowed
        """
        if action in self.RISKY_ACTIONS:
            logger.warning(f"Risky action: {action}")
            return not self.confirmation_required

        if action in self.SAFE_ACTIONS:
            return True

        logger.warning(f"Unknown action: {action}")
        return False

    def request_confirmation(
        self, action: str, parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Request user confirmation for action.

        Args:
            action: Action name
            parameters: Action parameters

        Returns:
            True if confirmed
        """
        prompt = f"\n⚠️  Risky action detected: {action}"
        if parameters:
            prompt += f"\nParameters: {parameters}"
        prompt += "\nContinue? (yes/no): "

        response = input(prompt).lower().strip()
        confirmed = response in ["yes", "y"]

        logger.info(
            f"Confirmation request for '{action}': {confirmed}"
        )

        return confirmed

    def log_execution(
        self,
        action: str,
        success: bool,
        duration: float,
        details: Optional[str] = None,
    ) -> None:
        """Log command execution.

        Args:
            action: Action name
            success: Whether action succeeded
            duration: Execution duration
            details: Additional details
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "success": success,
            "duration": duration,
            "details": details,
        }
        self.execution_log.append(entry)
        logger.info(f"Execution logged: {action} ({'success' if success else 'failed'})")

    def get_execution_log(
        self, action_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get execution log.

        Args:
            action_filter: Filter by action (optional)

        Returns:
            Execution log
        """
        if action_filter:
            return [
                entry
                for entry in self.execution_log
                if entry["action"] == action_filter
            ]
        return self.execution_log.copy()

    def clear_log(self) -> None:
        """Clear execution log."""
        self.execution_log.clear()
        logger.info("Execution log cleared")
