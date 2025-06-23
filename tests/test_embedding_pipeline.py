import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.embedding_pipeline import split_documents, select_strategy
from langchain_core.documents import Document


def test_recursive_strategy():
    docs = [Document(page_content="a" * 1500)]
    strategy = select_strategy(docs)
    assert strategy == "recursive"
    chunks = split_documents(docs)
    assert len(chunks) > 1
    assert all(c.metadata["split_strategy"] == "recursive" for c in chunks)


def test_none_strategy():
    docs = [Document(page_content="short text")]
    strategy = select_strategy(docs)
    assert strategy == "none"
    chunks = split_documents(docs)
    assert len(chunks) == 1
    assert chunks[0].page_content == "short text"
    assert chunks[0].metadata["split_strategy"] == "none"


def test_sentence_strategy():
    docs = [Document(page_content="Sentence one. " * 20)]
    strategy = select_strategy(docs)
    assert strategy == "sentence"
    chunks = split_documents(docs)
    assert len(chunks) > 1
    assert all(c.metadata["split_strategy"] == "sentence" for c in chunks)


def test_select_strategy_empty():
    assert select_strategy([]) == "none"


