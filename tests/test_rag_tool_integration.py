import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage

from ingestion import ingest
import rag_agent
import tool_agent


def test_rag_to_tool_flow(capsys):
    doc_text = "Sample integration document"

    # Ingest the document
    with patch("ingestion.ingest.load_files", return_value=[Document(page_content=doc_text)]), \
         patch("ingestion.ingest.load_gmail", return_value=[]), \
         patch("ingestion.ingest.OllamaEmbeddings"), \
         patch("ingestion.ingest.Qdrant") as fake_qdrant:
        vs = MagicMock()
        fake_qdrant.return_value = vs
        vs.add_texts.return_value = ["1"]
        ingest(directory="dummy")
        assert vs.add_texts.called

    # Retrieve the document via rag_agent
    state = {"messages": [HumanMessage(content="where is the sample?" )], "context_docs": []}
    fake_retriever = MagicMock()
    fake_retriever.invoke.return_value = [Document(page_content=doc_text)]
    with patch("rag_agent.retriever", fake_retriever):
        ctx = rag_agent.retrieve_context(state)
    assert doc_text in ctx["context_docs"][0]

    fake_llm = MagicMock()
    fake_llm.chat.return_value = AIMessage(content="answer")
    with patch("rag_agent.get_default_client", return_value=fake_llm):
        rag_agent.answer_step({**state, "context_docs": ctx["context_docs"]})

    # Execute a simple tool using tool_agent
    fake_agent = MagicMock()

    def _fake_invoke(st, config=None):
        return {"messages": st["messages"] + [AIMessage(content=f"tool executed: {st['messages'][0].content}")]}

    fake_agent.invoke.side_effect = _fake_invoke
    with patch("tool_agent.build_agent", return_value=fake_agent), \
         patch("tool_agent.Langfuse"), \
         patch("tool_agent.CallbackHandler"):
        tool_agent.main(ctx["context_docs"][0])

    captured = capsys.readouterr()
    assert doc_text in captured.out

