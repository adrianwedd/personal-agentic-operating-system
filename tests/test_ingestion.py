import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import patch, MagicMock

from langchain_experimental.graph_transformers import LLMGraphTransformer

from ingestion import ingest
from ingestion.ingest import get_text_chunks


def test_get_text_chunks():
    from langchain_core.documents import Document
    docs = [Document(page_content="a" * 1500)]
    chunks = get_text_chunks(docs)
    assert len(chunks) > 1


def test_ingest_pipeline():
    from langchain_core.documents import Document
    fake_doc = Document(page_content="hello world")
    with patch("ingestion.ingest.load_gmail", return_value=[fake_doc]) as lg, \
         patch("ingestion.ingest.load_files", return_value=[fake_doc]) as lf, \
         patch("ingestion.ingest.OllamaEmbeddings") as embed, \
         patch("ingestion.ingest.Qdrant") as qdrant:
        mock_vs = MagicMock()
        qdrant.return_value = mock_vs
        mock_vs.add_texts.return_value = ["1"]
        ingest("test", "./data")
        assert mock_vs.add_texts.called


def test_llm_graph_transformer_schema():
    from langchain_core.documents import Document
    from langchain_experimental.graph_transformers.llm import Node, GraphDocument, _Graph
    from ingestion.build_pkg import ALLOWED_NODES
    doc = Document(
        page_content=
        "John Doe worked on Project Phoenix with ACME Corp and discussed the budget"
    )

    fake_llm = MagicMock()
    transformer = LLMGraphTransformer(fake_llm, allowed_nodes=ALLOWED_NODES)
    fake_graph = _Graph(
        nodes=[
            Node(id="John Doe", type="Person"),
            Node(id="Project Phoenix", type="Project"),
            Node(id="ACME Corp", type="Company"),
            Node(id="Budget", type="Finance Topic"),
        ],
        relationships=[],
    )
    with patch.object(transformer, "chain") as chain:
        chain.invoke.return_value = {"parsed": fake_graph}
        gdocs = transformer.convert_to_graph_documents([doc])

    node_types = {n.type for n in gdocs[0].nodes}
    assert "Finance Topic" not in node_types
    assert {"Person", "Project", "Company"}.issubset(node_types)
