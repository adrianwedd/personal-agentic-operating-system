from __future__ import annotations

"""Build the Personal Knowledge Graph from ingested documents."""
import os
from typing import List, Tuple
from langchain_core.documents import Document

from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.chat_models import ChatOllama
from neo4j import GraphDatabase
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

# Support running as a script (`python ingestion/build_pkg.py`) or module
if __package__:
    from .pkg_config import (
        ALLOWED_NODE_TYPES,
        ALLOWED_EDGE_TYPES,
        install_constraints,
    )
else:  # pragma: no cover - direct script execution
    from pkg_config import (  # type: ignore
        ALLOWED_NODE_TYPES,
        ALLOWED_EDGE_TYPES,
        install_constraints,
    )

    from loaders import load_gmail, load_files  # type: ignore

if __package__:
    from .loaders import load_gmail, load_files



def _load_docs(gmail_query: str | None, directory: str | None) -> List[Document]:
    """Load documents from Gmail and/or a local directory.

    Parameters
    ----------
    gmail_query : str, optional
        Search query used to pull messages from Gmail.
    directory : str, optional
        Path to a directory of text files to ingest.

    Returns
    -------
    List[Document]
        Combined list of loaded documents.
    """

    docs: List[Document] = []
    if gmail_query:
        docs.extend(load_gmail(gmail_query))
    if directory:
        docs.extend(load_files(directory))
    return docs


def _convert_filter(
    transformer: LLMGraphTransformer,
    docs,
    handler: CallbackHandler,
) -> List[Tuple[str, str, str, str, str]]:
    """Convert documents to triples and remove unsupported entity types.

    Parameters
    ----------
    transformer : LLMGraphTransformer
        Transformer used to extract entities and relations from documents.
    docs : Iterable[Document]
        Documents to transform.
    handler : CallbackHandler
        Langfuse callback handler for instrumentation.

    Returns
    -------
    List[Tuple[str, str, str, str, str]]
        Filtered list of triples ``(source_id, source_type, relation, target_id, target_type)``.
    """
    graph_docs = transformer.convert_to_graph_documents(
        docs, config={"callbacks": [handler]}
    )
    triples: List[Tuple[str, str, str, str, str]] = []
    for gdoc in graph_docs:
        for rel in gdoc.relationships:
            if (
                rel.type in ALLOWED_EDGE_TYPES
                and rel.source.type in ALLOWED_NODE_TYPES
                and rel.target.type in ALLOWED_NODE_TYPES
            ):
                triples.append(
                    (
                        rel.source.id,
                        rel.source.type,
                        rel.type,
                        rel.target.id,
                        rel.target.type,
                    )
                )
    return triples


def _store_triples(triples: List[Tuple[str, str, str, str, str]]) -> None:
    """Persist triples in Neo4j.

    Parameters
    ----------
    triples : List[Tuple[str, str, str, str, str]]
        Output from :func:`_convert_filter` representing edges in the form
        ``(source_id, source_type, relation, target_id, target_type)``.
    """

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
        session.execute_write(install_constraints)
        for s, stype, r, t, ttype in triples:
            session.run(
                f"""
                MERGE (s:{stype} {{name:$s}})
                MERGE (o:{ttype} {{name:$o}})
                MERGE (s)-[:{r}]->(o)
                """,
                {"s": s, "o": t},
            )


def build_pkg(gmail_query: str | None = None, directory: str | None = None) -> int:
    """Extract graph triples from documents and store them in Neo4j.

    Parameters
    ----------
    gmail_query : str, optional
        Gmail search query used to fetch messages for graph extraction.
    directory : str, optional
        Directory containing text files to include in the graph build.

    Returns
    -------
    int
        Number of triples successfully stored.
    """
    docs = _load_docs(gmail_query, directory)
    if not docs:
        print("No documents loaded")
        return

    llm = ChatOllama()
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=list(ALLOWED_NODE_TYPES),
        allowed_relationships=list(ALLOWED_EDGE_TYPES),
    )
    langfuse = Langfuse()
    handler = CallbackHandler(langfuse)
    triples = _convert_filter(transformer, docs, handler)

    _store_triples(triples)
    print(f"Stored {len(triples)} triples in Neo4j")
    return len(triples)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build personal knowledge graph")
    parser.add_argument("--gmail-query", default=None)
    parser.add_argument("--directory", default=None)
    args = parser.parse_args()

    added = build_pkg(args.gmail_query, args.directory)
    print(f"added {added} triples")
