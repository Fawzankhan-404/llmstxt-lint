"""llmstxt-lint: validate llms.txt files."""
from .linter import Issue, lint_text

__all__ = ["Issue", "lint_text"]
__version__ = "0.2.0"
