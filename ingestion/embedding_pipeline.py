from __future__ import annotations

"""Dynamic embedding pipeline with multiple split strategies."""

from typing import Iterable, List
import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


RECURSIVE_THRESHOLD = 1200
SENTENCE_THRESHOLD = 200

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def select_strategy(
    docs: Iterable[Document],
    *,
    recursive_threshold: int = RECURSIVE_THRESHOLD,
    sentence_threshold: int = SENTENCE_THRESHOLD,
) -> str:
    """Choose a splitting strategy based on average document length."""
    docs = list(docs)
    if not docs:
        return "none"
    avg_len = sum(len(d.page_content) for d in docs) / len(docs)
    if avg_len > recursive_threshold:
        return "recursive"
    if avg_len > sentence_threshold:
        return "sentence"
    return "none"


def _split_sentence(text: str) -> List[str]:
    return [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]


def split_documents(
    docs: Iterable[Document],
    *,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    recursive_threshold: int = RECURSIVE_THRESHOLD,
    sentence_threshold: int = SENTENCE_THRESHOLD,
) -> List[Document]:
    """Split documents using an adaptive strategy.

    Returned chunks contain a ``split_strategy`` metadata field.
    """

    docs = list(docs)
    strategy = select_strategy(
        docs,
        recursive_threshold=recursive_threshold,
        sentence_threshold=sentence_threshold,
    )

    chunks: List[Document] = []
    if strategy == "recursive":
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        chunks = splitter.split_documents(docs)
    elif strategy == "sentence":
        for doc in docs:
            for sent in _split_sentence(doc.page_content):
                chunks.append(Document(page_content=sent, metadata=dict(doc.metadata)))
    else:  # "none"
        chunks = [Document(page_content=d.page_content, metadata=dict(d.metadata)) for d in docs]

    for chunk in chunks:
        meta = chunk.metadata or {}
        meta["split_strategy"] = strategy
        chunk.metadata = meta

    return chunks


__all__ = ["split_documents", "select_strategy"]

