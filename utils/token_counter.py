from __future__ import annotations

"""Utility to approximate token counts and trim message history."""
from typing import List

try:
    import tiktoken

    _encoder = tiktoken.get_encoding("cl100k_base")
except Exception:  # pragma: no cover - tiktoken optional
    _encoder = None

from langchain_core.messages import BaseMessage


def count_tokens(text: str) -> int:
    """Return the token count using tiktoken if available."""
    if _encoder:
        return len(_encoder.encode(text))
    return len(text.split())


def count_message_tokens(messages: List[BaseMessage]) -> int:
    """Count tokens across a list of messages."""
    return sum(count_tokens(m.content) for m in messages)


def trim_messages(messages: List[BaseMessage], max_tokens: int = 8192) -> List[BaseMessage]:
    """Trim oldest messages until total token count fits within limit."""
    total = count_message_tokens(messages)
    trimmed = list(messages)
    while trimmed and total > max_tokens:
        msg = trimmed.pop(0)
        total -= count_tokens(msg.content)
    return trimmed
