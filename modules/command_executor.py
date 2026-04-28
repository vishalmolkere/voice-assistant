"""Command Execution Module for system operations."""

import json
import logging
import os
import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Execute system commands and operations."""

    SUPPORTED_ACTIONS = [
        "open_folder",
        "create_project",
        "write_code",
        "run_code",
        "execute_system",
        "exit",
    ]

    def __init__(self, sandbox_mode: bool = True):
        """Initialize command executor.

        Args:
            sandbox_mode: Enable sandbox safety checks
        """
        self.sandbox_mode = sandbox_mode
        self.os_type = self._detect_os()
        logger.info(f"CommandExecutor initialized (OS: {self.os_type})")

    def _detect_os(self) -> str:
        """Detect operating system.

        Returns:
            OS type (macos, linux, windows)
        """
        system = platform.system()
        if system == "Darwin":
            return "macos"
        elif system == "Linux":
            return "linux"
        elif system == "Windows":
            return "windows"
        return "unknown"

    def execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command.

        Args:
            command: Command dictionary with action and parameters

        Returns:
            Execution result
        """
        try:
            action = command.get("action")
            parameters = command.get("parameters", {})

            if action not in self.SUPPORTED_ACTIONS:
                logger.warning(f"Unsupported action: {action}")
                return {
                    "success": False,
                    "error": f"Unsupported action: {action}",
                }

            logger.info(f"Executing: {action} with {parameters}")

            # Execute based on action
            if action == "open_folder":
                return self._open_folder(parameters.get("path"))
            elif action == "create_project":
                return self._create_project(
                    parameters.get("name"),
                    parameters.get("language", "python"),
                )
            elif action == "write_code":
                return self._write_code(
                    parameters.get("code"),
                    parameters.get("filename"),
                )
            elif action == "run_code":
                return self._run_code(parameters.get("path"))
            elif action == "execute_system":
                return self._execute_system(parameters.get("command"))
            elif action == "exit":
                return {"success": True, "message": "Exiting assistant"}

        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {"success": False, "error": str(e)}

    def _open_folder(self, path: str) -> Dict[str, Any]:
        """Open folder in file explorer.

        Args:
            path: Folder path

        Returns:
            Execution result
        """
        try:
            # Expand ~ to home directory
            expanded_path = os.path.expanduser(path)
            full_path = Path(expanded_path).resolve()

            if not full_path.exists():
                logger.warning(f"Path does not exist: {full_path}")
                return {
                    "success": False,
                    "error": f"Path does not exist: {path}",
                }

            logger.info(f"Opening folder: {full_path}")

            if self.os_type == "macos":
                subprocess.run(["open", str(full_path)], check=True)
            elif self.os_type == "linux":
                subprocess.run(["xdg-open", str(full_path)], check=True)
            elif self.os_type == "windows":
                os.startfile(str(full_path))

            return {"success": True, "message": f"Opened: {full_path}"}

        except Exception as e:
            logger.error(f"Failed to open folder: {e}")
            return {"success": False, "error": str(e)}

    def _create_project(self, name: str, language: str) -> Dict[str, Any]:
        """Create project structure.

        Args:
            name: Project name
            language: Programming language

        Returns:
            Execution result
        """
        try:
            project_dir = Path.cwd() / name
            project_dir.mkdir(exist_ok=True)

            if language == "python":
                (project_dir / "main.py").write_text(
                    '"""Main module."""\n\ndef main():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()\n'
                )
                (project_dir / "requirements.txt").write_text("")
                (project_dir / ".gitignore").write_text(
                    "__pycache__/\n*.pyc\n.env\nvenv/\n"
                )
            elif language == "java":
                src_dir = project_dir / "src"
                src_dir.mkdir(exist_ok=True)
                (src_dir / "Main.java").write_text(
                    'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}\n'
                )

            logger.info(f"Created {language} project: {project_dir}")
            return {
                "success": True,
                "message": f"Project created at {project_dir}",
                "path": str(project_dir),
            }

        except Exception as e:
            logger.error(f"Project creation error: {e}")
            return {"success": False, "error": str(e)}

    def _write_code(self, code: str, filename: str) -> Dict[str, Any]:
        """Write code to file.

        Args:
            code: Code content
            filename: Output filename

        Returns:
            Execution result
        """
        try:
            file_path = Path.cwd() / filename
            file_path.write_text(code)
            logger.info(f"Code written to {file_path}")
            return {
                "success": True,
                "message": f"Code saved to {file_path}",
                "path": str(file_path),
            }
        except Exception as e:
            logger.error(f"Code write error: {e}")
            return {"success": False, "error": str(e)}

    def _run_code(self, path: str) -> Dict[str, Any]:
        """Run Python script.

        Args:
            path: Script path

        Returns:
            Execution result
        """
        try:
            script_path = Path(path)
            if not script_path.exists():
                return {"success": False, "error": f"File not found: {path}"}

            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            logger.info(f"Script executed: {path}")
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
            }

        except subprocess.TimeoutExpired:
            logger.error("Script execution timeout")
            return {"success": False, "error": "Script execution timeout"}
        except Exception as e:
            logger.error(f"Script execution error: {e}")
            return {"success": False, "error": str(e)}

    def _execute_system(self, command: str) -> Dict[str, Any]:
        """Execute system command.

        Args:
            command: System command

        Returns:
            Execution result
        """
        try:
            if self.sandbox_mode:
                logger.warning(
                    f"System command blocked in sandbox mode: {command}"
                )
                return {
                    "success": False,
                    "error": "System commands blocked in sandbox mode",
                }

            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )

            logger.info(f"System command executed: {command}")
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
            }

        except subprocess.TimeoutExpired:
            logger.error("System command timeout")
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            logger.error(f"System command error: {e}")
            return {"success": False, "error": str(e)}
