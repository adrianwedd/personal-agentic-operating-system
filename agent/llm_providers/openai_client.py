from __future__ import annotations

"""OpenAI API client adhering to LLMClient interface."""

import os
from typing import Iterable, List

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import AIMessage, BaseMessage
import tiktoken

from .base import LLMClient


class OpenAIClient(LLMClient):
    """Implementation using OpenAI's API via langchain-openai."""

    def __init__(self) -> None:
        model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        embedding_model = os.environ.get("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        self.chat_model = ChatOpenAI(model=model, api_key=os.environ.get("OPENAI_API_KEY"))
        self.embed_model = OpenAIEmbeddings(model=embedding_model, api_key=os.environ.get("OPENAI_API_KEY"))
        self._encoder = tiktoken.encoding_for_model(model)

    def chat(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        return self.chat_model.invoke(messages, **kwargs)

    def stream_chat(self, messages: List[BaseMessage], **kwargs) -> Iterable[AIMessage]:
        yield from self.chat_model.stream(messages, **kwargs)

    def embed(self, texts: List[str]) -> List[List[float]]:
        return self.embed_model.embed_documents(texts)

    def count_tokens(self, messages: List[BaseMessage]) -> int:
        return sum(len(self._encoder.encode(m.content)) for m in messages)
