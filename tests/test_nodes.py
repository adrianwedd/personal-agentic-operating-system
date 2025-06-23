import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

import agent.nodes as nodes


def test_plan_step_uses_pkg():
    state = {"messages": [HumanMessage(content="plan this")]}
    fake_llm = MagicMock()
    fake_llm.invoke.return_value = AIMessage(content="- step1\n- step2")
    fake_driver = MagicMock()
    fake_session = fake_driver.session.return_value.__enter__.return_value
    fake_session.run.return_value = [{"entity": "ProjectX"}]
    with patch("agent.nodes.ChatOllama", return_value=fake_llm), patch(
        "agent.nodes.GraphDatabase.driver", return_value=fake_driver
    ):
        out = nodes.plan_step(state)
    assert out["tasks"] == ["step1", "step2"]
    assert fake_session.run.called


def test_retrieve_context_returns_metadata():
    state = {"messages": [HumanMessage(content="hello")]}
    fake_driver = MagicMock()
    fake_session = fake_driver.session.return_value.__enter__.return_value
    fake_session.run.return_value = [{"id": "1", "entity": "Alice"}]
    fake_doc = MagicMock()
    fake_doc.page_content = "hi"
    fake_retriever = MagicMock()
    fake_retriever.invoke.return_value = [fake_doc]
    with patch("agent.nodes.GraphDatabase.driver", return_value=fake_driver), patch(
        "agent.nodes.retriever", fake_retriever
    ):
        out = nodes.retrieve_context(state)
    assert out["context_docs"] == ["hi"]
    assert out["graph_metadata"] == [{"doc_id": "1", "entity": "Alice"}]
