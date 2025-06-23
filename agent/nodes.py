from __future__ import annotations

"""Agent nodes with PKG-aware planning and retrieval."""
from typing import List, Dict, TypedDict, Any

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from neo4j import GraphDatabase


class AgentState(TypedDict, total=False):
    messages: List[BaseMessage]
    tasks: List[str]
    context_docs: List[str]
    graph_metadata: List[Dict[str, Any]]


# --- PKG Query Helpers ---------------------------------------------------------


def _query_pkg(query: str) -> tuple[list[str], list[dict]]:
    """Return related document IDs and metadata from the graph."""
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
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


# --- Vector Retriever ----------------------------------------------------------


def _build_retriever() -> any:
    client = QdrantClient(url="http://localhost:6333")
    vectorstore = Qdrant(
        client=client,
        collection_name="ingestion",
        embeddings=OllamaEmbeddings(),
    )
    return vectorstore.as_retriever()


retriever = _build_retriever()


# --- Nodes --------------------------------------------------------------------


def retrieve_context(state: AgentState) -> Dict[str, Any]:
    """Retrieve docs using PKG guidance and return metadata."""
    query = state["messages"][-1].content
    doc_ids, meta = _query_pkg(query)
    if doc_ids:
        docs = retriever.invoke(query, search_kwargs={"filter": {"id": doc_ids}})
    else:
        docs = retriever.invoke(query)
    return {
        "context_docs": [d.page_content for d in docs],
        "graph_metadata": meta,
    }


def plan_step(state: AgentState) -> Dict[str, Any]:
    """Generate a task list informed by PKG context."""
    prompt = state["messages"][-1].content
    _, meta = _query_pkg(prompt)
    parts = []
    for m in meta:
        if "email" in m:
            parts.append(f"{m['entity']} <{m['email']}>")
        else:
            parts.append(m["entity"])
    context = ", ".join(parts)
    llm = ChatOllama()
    user_prompt = (
        f"Known entities: {context}\nUser request: {prompt}\nPlan as bullet list."
    )
    ai: AIMessage = llm.invoke([HumanMessage(content=user_prompt)])
    tasks = [t.strip("- ") for t in ai.content.splitlines() if t.strip()]
    return {"tasks": tasks}
