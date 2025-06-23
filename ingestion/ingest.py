"""Ingestion script for populating Qdrant with local data and emails."""
from __future__ import annotations

import os
from typing import Iterable, List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

from .loaders import load_gmail, load_files


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def get_text_chunks(docs: Iterable) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return [chunk.page_content for chunk in splitter.split_documents(list(docs))]


def ingest(gmail_query: str | None = None, directory: str | None = None) -> None:
    """Run the ingestion pipeline."""
    documents = []
    if gmail_query:
        documents.extend(load_gmail(gmail_query))
    if directory:
        documents.extend(load_files(directory))

    if not documents:
        print("No documents loaded")
        return

    texts = get_text_chunks(documents)

    embeddings = OllamaEmbeddings()
    client = QdrantClient(url=os.environ.get("QDRANT_URL", "http://localhost:6333"))
    vectorstore = Qdrant(client=client, collection_name="ingestion", embeddings=embeddings)

    ids = vectorstore.add_texts(texts)
    print(f"Stored {len(ids)} chunks in Qdrant collection 'ingestion'")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run ingestion")
    parser.add_argument("--gmail-query", help="Gmail search query", default=None)
    parser.add_argument("--directory", help="Directory of files to ingest", default=None)
    args = parser.parse_args()

    ingest(args.gmail_query, args.directory)
