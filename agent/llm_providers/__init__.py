from __future__ import annotations

"""LLM client registry."""

import os
from typing import Type

from .base import LLMClient
from .ollama_client import OllamaClient
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient
from .deepseek_client import DeepSeekClient

__all__ = [
    "LLMClient",
    "OllamaClient",
    "OpenAIClient",
    "GeminiClient",
    "DeepSeekClient",
    "get_default_client",
]


_CLIENTS: dict[str, Type[LLMClient]] = {
    "ollama": OllamaClient,
    "openai": OpenAIClient,
    "gemini": GeminiClient,
    "deepseek": DeepSeekClient,
}


def get_default_client() -> LLMClient:
    """Instantiate the LLM client based on env vars."""
    backend = os.environ.get("LLM_BACKEND", "ollama").lower()
    cls = _CLIENTS.get(backend, OllamaClient)
    return cls()
