from __future__ import annotations

"""Google Gemini client using google-generativeai SDK."""

import os
from typing import Iterable, List

from langchain_core.messages import AIMessage, BaseMessage

from .base import LLMClient

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional dependency
    genai = None


class GeminiClient(LLMClient):
    """Thin wrapper around the Gemini API."""

    def __init__(self) -> None:
        if genai is None:
            raise ImportError("google-generativeai required for Gemini backend")
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = os.environ.get("GEMINI_MODEL", "gemini-pro")
        self.chat_model = genai.GenerativeModel(model)

    def chat(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        content = "\n".join(m.content for m in messages)
        resp = self.chat_model.generate_content(content)
        return AIMessage(content=resp.text)

    def stream_chat(self, messages: List[BaseMessage], **kwargs) -> Iterable[AIMessage]:
        content = "\n".join(m.content for m in messages)
        stream = self.chat_model.generate_content(content, stream=True)
        for chunk in stream:
            yield AIMessage(content=chunk.text)

    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("Gemini does not support embeddings")

    def count_tokens(self, messages: List[BaseMessage]) -> int:
        content = "\n".join(m.content for m in messages)
        return len(content.split())
