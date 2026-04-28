"""Code Generation Module using OpenAI GPT."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import openai

logger = logging.getLogger(__name__)


class CodeGenerator:
    """Generate code using GPT."""

    SUPPORTED_LANGUAGES = ["python", "java", "javascript", "bash", "cpp", "c"]

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.5,
        output_dir: str = "./generated_code",
    ):
        """Initialize code generator.

        Args:
            api_key: OpenAI API key
            model: GPT model to use
            temperature: Temperature for generation
            output_dir: Output directory for generated code
        """
        openai.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"CodeGenerator initialized")

    def generate(
        self,
        prompt: str,
        language: str = "python",
        save: bool = True,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate code.

        Args:
            prompt: Code generation prompt
            language: Programming language
            save: Save to file
            filename: Output filename

        Returns:
            Generated code and metadata
        """
        try:
            if language not in self.SUPPORTED_LANGUAGES:
                logger.warning(f"Unsupported language: {language}")
                return {
                    "success": False,
                    "error": f"Unsupported language: {language}",
                }

            logger.info(f"Generating {language} code: {prompt[:50]}...")

            # Build system prompt
            system_prompt = f"""
            You are an expert {language} developer. 
            Generate clean, well-documented, production-ready code.
            Include docstrings/comments.
            Follow best practices for {language}.
            Only respond with code, no explanations.
            """

            # Call GPT
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=2000,
            )

            code = response["choices"][0]["message"]["content"]
            logger.info(f"Code generated: {len(code)} characters")

            # Save if requested
            file_path = None
            if save:
                if not filename:
                    filename = f"generated_code.{self._get_extension(language)}"
                file_path = self.output_dir / filename
                file_path.write_text(code)
                logger.info(f"Code saved to {file_path}")

            return {
                "success": True,
                "code": code,
                "language": language,
                "filename": filename,
                "path": str(file_path) if file_path else None,
            }

        except Exception as e:
            logger.error(f"Code generation error: {e}")
            return {"success": False, "error": str(e)}

    def _get_extension(self, language: str) -> str:
        """Get file extension for language.

        Args:
            language: Programming language

        Returns:
            File extension
        """
        extensions = {
            "python": "py",
            "java": "java",
            "javascript": "js",
            "bash": "sh",
            "cpp": "cpp",
            "c": "c",
        }
        return extensions.get(language, "txt")

    def generate_with_tests(
        self, prompt: str, language: str = "python"
    ) -> Dict[str, Any]:
        """Generate code with unit tests.

        Args:
            prompt: Code generation prompt
            language: Programming language

        Returns:
            Generated code and tests
        """
        try:
            # Generate main code
            code_result = self.generate(prompt, language, save=False)
            if not code_result["success"]:
                return code_result

            code = code_result["code"]

            # Generate tests
            test_prompt = f"Write unit tests for this {language} code:\n{code}"
            test_response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Generate unit tests only."},
                    {"role": "user", "content": test_prompt},
                ],
                temperature=0.3,
                max_tokens=1500,
            )

            tests = test_response["choices"][0]["message"]["content"]
            logger.info(f"Tests generated for {language} code")

            return {
                "success": True,
                "code": code,
                "tests": tests,
                "language": language,
            }

        except Exception as e:
            logger.error(f"Code generation with tests error: {e}")
            return {"success": False, "error": str(e)}
