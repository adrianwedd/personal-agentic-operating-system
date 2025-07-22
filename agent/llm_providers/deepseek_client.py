from __future__ import annotations

"""DeepSeek API client via raw HTTP requests."""

import os
from typing import Iterable, List

import requests
from langchain_core.messages import AIMessage, BaseMessage

from .base import LLMClient


class DeepSeekError(Exception):
    """Custom error raised when DeepSeek API calls fail."""

    pass


class DeepSeekClient(LLMClient):
    """Simple wrapper for DeepSeek LLM endpoints."""

    BASE_URL = "https://api.deepseek.com"

    def __init__(self) -> None:
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

    def _post(self, endpoint: str, json: dict, **kwargs) -> requests.Response:
        """Send a POST request and convert any errors to ``DeepSeekError``."""
        try:
            resp = requests.post(
                f"{self.BASE_URL}{endpoint}",
                headers=self._headers(),
                json=json,
                timeout=30,
                **kwargs,
            )
            resp.raise_for_status()
            return resp
        except requests.Timeout as exc:
            raise DeepSeekError("DeepSeek request timed out") from exc
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response else "N/A"
            text = exc.response.text if getattr(exc, "response", None) else str(exc)
            raise DeepSeekError(f"DeepSeek API error {status}: {text}") from exc
        except requests.RequestException as exc:
            raise DeepSeekError(f"DeepSeek request failed: {exc}") from exc

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": "\n".join(m.content for m in messages)}
            ],
        }
        resp = self._post("/chat/completions", json=data)
        content = (
            resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        )
        return AIMessage(content=content)

    def stream_chat(self, messages: List[BaseMessage], **kwargs) -> Iterable[AIMessage]:
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": "\n".join(m.content for m in messages)}
            ],
            "stream": True,
        }
        resp = self._post("/chat/completions", json=data, stream=True)
        with resp:
            for line in resp.iter_lines():
                if line:
                    yield AIMessage(content=line.decode())

    def embed(self, texts: List[str]) -> List[List[float]]:
        resp = self._post(
            "/embeddings",
            json={"model": self.model, "input": texts},
        )
        return [e["embedding"] for e in resp.json().get("data", [])]

    def count_tokens(self, messages: List[BaseMessage]) -> int:
        content = "\n".join(m.content for m in messages)
        return len(content.split())
