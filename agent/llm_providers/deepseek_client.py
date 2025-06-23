from __future__ import annotations

"""DeepSeek API client via raw HTTP requests."""

import os
from typing import Iterable, List

import requests
from langchain_core.messages import AIMessage, BaseMessage

from .base import LLMClient


class DeepSeekClient(LLMClient):
    """Simple wrapper for DeepSeek LLM endpoints."""

    BASE_URL = "https://api.deepseek.com"

    def __init__(self) -> None:
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def chat(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": "\n".join(m.content for m in messages)}],
        }
        resp = requests.post(f"{self.BASE_URL}/chat/completions", headers=self._headers(), json=data, timeout=30)
        resp.raise_for_status()
        content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        return AIMessage(content=content)

    def stream_chat(self, messages: List[BaseMessage], **kwargs) -> Iterable[AIMessage]:
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": "\n".join(m.content for m in messages)}],
            "stream": True,
        }
        with requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self._headers(),
            json=data,
            stream=True,
            timeout=30,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    yield AIMessage(content=line.decode())

    def embed(self, texts: List[str]) -> List[List[float]]:
        resp = requests.post(
            f"{self.BASE_URL}/embeddings",
            headers=self._headers(),
            json={"model": self.model, "input": texts},
            timeout=30,
        )
        resp.raise_for_status()
        return [e["embedding"] for e in resp.json().get("data", [])]

    def count_tokens(self, messages: List[BaseMessage]) -> int:
        content = "\n".join(m.content for m in messages)
        return len(content.split())
