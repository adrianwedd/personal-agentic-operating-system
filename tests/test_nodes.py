import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

import agent.nodes as nodes
import hitl_cli
import json


def test_plan_step_uses_pkg():
    state = {"messages": [HumanMessage(content="plan this")]}
    fake_llm = MagicMock()
    fake_llm.chat.return_value = AIMessage(content="- step1\n- step2")
    fake_driver = MagicMock()
    fake_session = fake_driver.session.return_value.__enter__.return_value
    fake_session.run.return_value = [{"entity": "ProjectX"}]
    import importlib
    rc = importlib.import_module("agent.retrieve_context")
    with patch("agent.nodes.get_default_client", return_value=fake_llm), patch.object(rc.GraphDatabase, "driver", return_value=fake_driver):
        out = nodes.plan_step(state)
    assert out["tasks"] == ["step1", "step2"]
    assert fake_session.run.called


def test_plan_step_includes_email_metadata():
    state = {"messages": [HumanMessage(content="email Jane")]}

    class FakeLLM:
        def __init__(self):
            self.last_input = None

        def chat(self, msgs, *args, **kwargs):
            self.last_input = "\n".join(m.content for m in msgs)
            return AIMessage(content="- draft_email(to='jane.d@example.com')")

    fake_driver = MagicMock()
    fake_session = fake_driver.session.return_value.__enter__.return_value
    fake_session.run.return_value = [
        {"entity": "Jane Doe", "email": "jane.d@example.com"}
    ]

    llm = FakeLLM()
    import importlib
    rc = importlib.import_module("agent.retrieve_context")
    with patch("agent.nodes.get_default_client", return_value=llm), patch.object(rc.GraphDatabase, "driver", return_value=fake_driver):
        out = nodes.plan_step(state)

    assert "jane.d@example.com" in llm.last_input
    assert out["tasks"] == ["draft_email(to='jane.d@example.com')"]


def test_retrieve_context_returns_metadata():
    state = {"messages": [HumanMessage(content="hello")]}
    fake_driver = MagicMock()
    fake_session = fake_driver.session.return_value.__enter__.return_value
    fake_session.run.return_value = [{"id": "1", "entity": "Alice"}]
    fake_doc = MagicMock()
    fake_doc.page_content = "hi"
    fake_retriever = MagicMock()
    fake_retriever.invoke.return_value = [fake_doc]
    import importlib
    rc = importlib.import_module("agent.retrieve_context")
    with patch.object(rc.GraphDatabase, "driver", return_value=fake_driver), patch(
        "agent.retrieve_context.retriever", fake_retriever
    ):
        out = nodes.retrieve_context(state)
    assert out["context_docs"] == ["hi"]
    assert out["graph_metadata"] == [{"doc_id": "1", "entity": "Alice"}]


def test_retrieve_context_filters_entities():
    state = {"messages": [HumanMessage(content="hello")]} 
    fake_driver = MagicMock()
    fake_session = fake_driver.session.return_value.__enter__.return_value
    fake_session.run.return_value = [{"entity": "Alice"}]

    alice_doc = MagicMock()
    alice_doc.page_content = "alice"
    bob_doc = MagicMock()
    bob_doc.page_content = "bob"

    def invoke_side_effect(query, search_kwargs=None):
        if search_kwargs and "filter" in search_kwargs:
            if "Alice" in search_kwargs["filter"]["must"][0]["match"].get("any", []):
                return [alice_doc]
        return [alice_doc, bob_doc]

    fake_retriever = MagicMock()
    fake_retriever.invoke.side_effect = invoke_side_effect

    import importlib
    rc = importlib.import_module("agent.retrieve_context")
    with patch.object(rc.GraphDatabase, "driver", return_value=fake_driver), patch(
        "agent.retrieve_context.retriever", fake_retriever
    ):
        out = nodes.retrieve_context(state)

    assert out["context_docs"] == ["alice"]


def test_filter_qdrant_fallback():
    import importlib
    rc = importlib.import_module("agent.retrieve_context")

    doc = MagicMock()
    doc.page_content = "hi"
    fake_retriever = MagicMock()
    fake_retriever.invoke.side_effect = [[], [doc]]

    with patch.object(rc, "retriever", fake_retriever), patch.object(rc, "logging") as lg:
        docs = rc.filter_qdrant_by_entities("hello", ["Alice"])

    assert docs == [doc]
    assert fake_retriever.invoke.call_count == 2
    assert lg.warning.called


def test_prioritise_applies_rules():
    state = {"tasks": ["pay invoice"], "messages": []}
    rules = {"patterns": [{"regex": "invoice", "priority": "med"}]}
    with patch("agent.nodes.load_priority_rules", return_value=rules), patch(
        "agent.nodes.add_task"
    ), patch("agent.nodes._score_with_llm", return_value=0.2):
        out = nodes.prioritise(state)
    t = out["tasks"][0]
    assert t["priority"] == "med"
    assert t["status"] == "READY"


def test_prioritise_llm_fallback():
    state = {"tasks": ["other task"], "messages": []}
    with patch("agent.nodes.load_priority_rules", return_value={}), patch(
        "agent.nodes.get_default_client"
    ) as get_llm, patch("agent.nodes._score_with_llm", return_value=0.3), patch(
        "agent.nodes._priority_from_score", return_value="low"
    ), patch("agent.nodes.add_task"):
        out = nodes.prioritise(state)
    assert get_llm.called
    assert out["tasks"][0]["priority"] == "low"


def test_execute_tool_sets_hitl(tmp_path):
    state = {
        "current_task": {
            "task_id": "1",
            "objective": "send email",
            "requires_hitl": True,
            "tool_calls": [],
            "subtasks": [],
        }
    }
    out = nodes.execute_tool(state)
    assert out["current_task"]["status"] in {"IN_PROGRESS", "DONE", "ERROR"}


def test_hitl_cli_logs_reflection(tmp_path, monkeypatch):
    queue_dir = tmp_path / "hitl"
    refl_dir = tmp_path / "logs"
    os.makedirs(queue_dir, exist_ok=True)
    state = {"current_task": {"task_id": "2"}}
    with open(queue_dir / "2.json", "w") as fh:
        json.dump(state, fh)

    monkeypatch.setattr("hitl_cli.QUEUE_DIR", str(queue_dir))
    monkeypatch.setattr("hitl_cli.REFLECT_DIR", str(refl_dir))

    class DummyStore:
        def __init__(self):
            self.texts = []

        def add_texts(self, texts, ids=None):
            self.texts.extend(texts)

    dummy = DummyStore()
    monkeypatch.setattr(
        "hitl_cli.Qdrant",
        lambda client, collection_name, embeddings: dummy,
    )
    monkeypatch.setattr("hitl_cli.QdrantClient", lambda url: None)
    monkeypatch.setattr("hitl_cli.OllamaEmbeddings", lambda: None)

    hitl_cli.process_queue(action="approved")
    logs = list(refl_dir.glob("*.jsonl"))
    assert logs, "reflection file created"
    assert dummy.texts
