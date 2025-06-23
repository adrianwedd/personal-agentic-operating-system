from __future__ import annotations

"""Dynamic embedding strategies based on document length."""
from typing import Iterable, List

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(docs: Iterable, threshold: int = 1000) -> List[str]:
    """Return list of chunks using adaptive splitting."""
    docs = list(docs)
    if not docs:
        return []
    avg_len = sum(len(d.page_content) for d in docs) / len(docs)
    if avg_len > threshold:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return [c.page_content for c in splitter.split_documents(docs)]
    return [d.page_content for d in docs]
