import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.embedding_pipeline import split_documents
from langchain_core.documents import Document


def test_split_documents_recursion():
    docs = [Document(page_content="a" * 3000)]
    chunks = split_documents(docs, threshold=200)
    assert len(chunks) > 1


def test_split_documents_short():
    docs = [Document(page_content="short text")]
    chunks = split_documents(docs)
    assert chunks == ["short text"]


