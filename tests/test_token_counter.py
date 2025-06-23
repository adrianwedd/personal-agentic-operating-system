import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import utils.token_counter as tc
from langchain_core.messages import HumanMessage, SystemMessage


def test_trim_messages_basic():
    msgs = [SystemMessage(content="a" * 10), HumanMessage(content="b" * 10)]
    trimmed = tc.trim_messages(msgs, max_tokens=1)
    assert len(trimmed) == 1
    assert isinstance(trimmed[0], HumanMessage)


