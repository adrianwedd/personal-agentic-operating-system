import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import patch, MagicMock

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
