from __future__ import annotations

"""Build the Personal Knowledge Graph from ingested documents."""
import os
from typing import List, Tuple

from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.chat_models import ChatOllama
from neo4j import GraphDatabase
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from .loaders import load_gmail, load_files

ALLOWED_NODES = ["Person", "Company", "Project", "Document"]
ALLOWED_RELATIONSHIPS = ["works_on", "communicates_with", "mentions"]


def _load_docs(gmail_query: str | None, directory: str | None):
    docs = []
    if gmail_query:
        docs.extend(load_gmail(gmail_query))
    if directory:
        docs.extend(load_files(directory))
    return docs


def _store_triples(triples: List[Tuple[str, str, str]]) -> None:
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URL", "bolt://localhost:7687"),
        auth=("neo4j", os.environ.get("NEO4J_PASSWORD", "password")),
    )
    with driver.session() as session:
        for s, r, t in triples:
            session.run(
                f"MERGE (a {{id:$s}}) MERGE (b {{id:$t}}) MERGE (a)-[:{r}]->(b)",
                s=s,
                t=t,
            )


def build_pkg(gmail_query: str | None = None, directory: str | None = None) -> None:
    """Extract graph triples from documents and store them."""
    docs = _load_docs(gmail_query, directory)
    if not docs:
        print("No documents loaded")
        return

    llm = ChatOllama()
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=ALLOWED_NODES,
        allowed_relationships=ALLOWED_RELATIONSHIPS,
    )
    langfuse = Langfuse()
    handler = CallbackHandler(langfuse)
    graph_docs = transformer.convert_to_graph_documents(
        docs, config={"callbacks": [handler]}
    )

    triples: List[Tuple[str, str, str]] = []
    for gdoc in graph_docs:
        for rel in gdoc.relationships:
            triples.append((rel.source.id, rel.type, rel.target.id))

    _store_triples(triples)
    print(f"Stored {len(triples)} triples in Neo4j")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build personal knowledge graph")
    parser.add_argument("--gmail-query", default=None)
    parser.add_argument("--directory", default=None)
    args = parser.parse_args()

    build_pkg(args.gmail_query, args.directory)
