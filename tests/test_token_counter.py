import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import utils.token_counter as tc
from langchain_core.messages import HumanMessage, SystemMessage


def test_trim_messages_basic():
    msgs = [SystemMessage(content="a"), HumanMessage(content="b")]
    trimmed = tc.trim_messages(msgs, max_tokens=1)
    assert len(trimmed) == 1
    assert isinstance(trimmed[0], HumanMessage)


def test_trim_long_prompt():
    long_text = "x " * 12000
    msgs = [HumanMessage(content=long_text)]
    trimmed = tc.trim_messages(msgs)
    total = tc.count_message_tokens(trimmed)
    assert total <= 8192


def test_count_tokens_fallback(monkeypatch):
    """Fallback to word split when tiktoken unavailable."""
    monkeypatch.setattr(tc, "_encoder", None)
    text = "hello world"
    assert tc.count_tokens(text) == 2


