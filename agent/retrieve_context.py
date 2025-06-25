from __future__ import annotations

"""Helper functions for PKG-aware retrieval."""

from typing import Tuple, List
import os
import logging

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain_core.documents import Document
from neo4j import GraphDatabase


# --- PKG Query --------------------------------------------------------------


def query_pkg(query: str) -> Tuple[List[str], List[dict]]:
    """Return related document IDs and metadata from the graph."""
    auth_str = os.environ.get("NEO4J_AUTH")
    if auth_str:
        user, pwd = auth_str.split("/", 1)
    else:
        user = "neo4j"
        pwd = os.environ.get("NEO4J_PASSWORD", "password")

    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URL", "bolt://localhost:7687"),
        auth=(user, pwd),
    )
    with driver.session() as session:
        result = session.run(
            """
            MATCH (d:Document)-[r]->(e)
            WHERE toLower(e.name) CONTAINS toLower($q)
            RETURN d.id AS id, e.name AS entity, e.email AS email
            LIMIT 10
            """,
            q=query,
        )
        data = []
        for record in result:
            entity = record.get("entity")
            doc_id = record.get("id")
            email = record.get("email")
            item = {"entity": entity}
            if doc_id is not None:
                item["doc_id"] = doc_id
            if email is not None:
                item["email"] = email
            data.append(item)
    doc_ids = [d["doc_id"] for d in data if "doc_id" in d]
    return doc_ids, data


# --- Vector Retriever -------------------------------------------------------


def _build_retriever() -> any:
    client = QdrantClient(url=os.environ.get("QDRANT_URL", "http://localhost:6333"))
    vectorstore = Qdrant(
        client=client,
        collection_name="ingestion",
        embeddings=OllamaEmbeddings(),
    )
    return vectorstore.as_retriever()


retriever = _build_retriever()


# --- Qdrant Filtering -------------------------------------------------------


def filter_qdrant_by_entities(query: str, entities: List[str]) -> List[Document]:
    """Return documents matching the query and entity metadata."""
    if entities:
        filter_ = {"must": [{"key": "entities", "match": {"any": entities}}]}
        docs = retriever.invoke(query, search_kwargs={"filter": filter_})
        if not docs:
            logging.warning("PKG filter returned 0 docs; falling back to vector search")
            docs = retriever.invoke(query)
    else:
        docs = retriever.invoke(query)
    return docs
