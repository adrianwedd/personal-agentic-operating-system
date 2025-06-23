"""Data loader utilities for the ingestion pipeline."""
from __future__ import annotations

from typing import List

from langchain_google_community import GMailLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents import Document


def load_gmail(query: str | None = None, *, label: str | None = None, max_results: int = 10) -> List[Document]:
    """Load messages from Gmail using the Google Community loader.

    Parameters
    ----------
    query : str, optional
        Gmail search query string.
    label : str, optional
        Restrict results to a specific label.
    max_results : int, default 10
        Limit the number of fetched messages.
    """
    loader = GMailLoader(query=query, label_ids=[label] if label else None, num_results=max_results)
    return loader.load()


def load_files(path: str) -> List[Document]:
    """Load documents from a local directory."""
    loader = DirectoryLoader(path)
    return loader.load()
