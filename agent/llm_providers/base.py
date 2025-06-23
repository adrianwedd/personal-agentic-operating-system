from __future__ import annotations

"""Abstract interface for LLM backends."""

from abc import ABC, abstractmethod
from typing import Iterable, List

from langchain_core.messages import BaseMessage, AIMessage


class LLMClient(ABC):
    """Unified interface for chat and embedding models."""

    @abstractmethod
    def chat(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        """Return a single chat completion."""

    @abstractmethod
    def stream_chat(self, messages: List[BaseMessage], **kwargs) -> Iterable[AIMessage]:
        """Yield chat completions as a stream."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return embeddings for a list of texts."""

    @abstractmethod
    def count_tokens(self, messages: List[BaseMessage]) -> int:
        """Count tokens for the provided messages."""
