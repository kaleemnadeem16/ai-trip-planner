from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Protocol


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...


@dataclass
class NoopLLMClient:
    """A no-network LLM client that raises errors to enforce agentic behavior.
    This app requires a real LLM to showcase agentic capabilities.
    """
    def complete(self, prompt: str) -> str:
        raise RuntimeError(
            "This is an agentic app that requires a working LLM. "
            "Please set OPENAI_API_KEY in your .env file to use the app."
        )
