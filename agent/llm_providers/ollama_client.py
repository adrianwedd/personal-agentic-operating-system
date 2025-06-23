from __future__ import annotations

"""LLMClient implementation using local Ollama."""

from typing import Iterable, List

from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.messages import AIMessage, BaseMessage

from .base import LLMClient
from utils.token_counter import count_message_tokens


class OllamaClient(LLMClient):
    """Wrapper around ChatOllama."""

    def __init__(self, model: str | None = None) -> None:
        self.chat_model = ChatOllama(model=model) if model else ChatOllama()
        self.embed_model = OllamaEmbeddings(model=model) if model else OllamaEmbeddings()

    def chat(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        return self.chat_model.invoke(messages, **kwargs)

    def stream_chat(self, messages: List[BaseMessage], **kwargs) -> Iterable[AIMessage]:
        yield from self.chat_model.stream(messages, **kwargs)

    def embed(self, texts: List[str]) -> List[List[float]]:
        return self.embed_model.embed_documents(texts)

    def count_tokens(self, messages: List[BaseMessage]) -> int:
        return count_message_tokens(messages)
