import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from unittest.mock import patch, MagicMock

import rag_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document


def test_retrieve_context():
    state = {"messages": [HumanMessage(content="foo")], "context_docs": []}
    fake_doc = Document(page_content="bar")
    fake_retriever = MagicMock()
    fake_retriever.invoke.return_value = [fake_doc]
    with patch("rag_agent.retriever", fake_retriever):
        out = rag_agent.retrieve_context(state)
    assert out["context_docs"] == ["bar"]


def test_answer_step():
    state = {"messages": [HumanMessage(content="hi")], "context_docs": ["ctx"]}
    fake_llm = MagicMock()
    fake_llm.chat.return_value = AIMessage(content="pong")
    with patch("rag_agent.get_default_client", return_value=fake_llm):
        out = rag_agent.answer_step(state)
    assert out["messages"][-1].content == "pong"
