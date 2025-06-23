from __future__ import annotations

"""Utility to approximate token counts and trim message history."""
from typing import List

from langchain_core.messages import BaseMessage


# Rough heuristic: split on whitespace.
# This avoids adding a heavy tokenizer dependency.
def count_tokens(text: str) -> int:
    return len(text.split())


def trim_messages(messages: List[BaseMessage], max_tokens: int = 4096) -> List[BaseMessage]:
    """Trim oldest messages until total token count fits within limit."""
    total = sum(count_tokens(m.content) for m in messages)
    trimmed = list(messages)
    while trimmed and total > max_tokens:
        msg = trimmed.pop(0)
        total -= count_tokens(msg.content)
    return trimmed
