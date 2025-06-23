from __future__ import annotations

"""Agent nodes with PKG-aware planning and retrieval."""
from typing import List, Dict, TypedDict, Any

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from neo4j import GraphDatabase
import os
import re
import yaml


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


PRIORITY_RULES_FILE = "rules/priority.yml"


def load_priority_rules(path: str = PRIORITY_RULES_FILE) -> dict:
    """Load priority rules from YAML, return empty dict if missing."""
    if not os.path.exists(path):
        return {}
    with open(path, "r") as fh:
        return yaml.safe_load(fh)


def apply_deterministic_rules(
    objective: str, sender: str | None, rules: dict
) -> str | None:
    """Return priority if a deterministic rule matches."""
    domain = sender.split("@")[-1] if sender else None
    if domain and domain in rules.get("bank_whitelist", []):
        return "high"
    for pat in rules.get("patterns", []):
        regex = pat.get("regex")
        priority = pat.get("priority")
        if regex and re.search(regex, objective, re.IGNORECASE):
            return priority
    return None


def prioritise(state: AgentState) -> Dict[str, Any]:
    """Assign priority to tasks using deterministic rules then LLM."""
    tasks = state.get("tasks", [])
    rules = load_priority_rules()
    llm = ChatOllama()
    results = []
    for t in tasks:
        if isinstance(t, dict):
            obj = t.get("objective", "")
            sender = t.get("sender")
        else:
            obj = t
            sender = None
        pr = apply_deterministic_rules(obj, sender, rules)
        if pr is None:
            prompt = f"Task: {obj}\nPriority options: critical, high, med, low."
            ai: AIMessage = llm.invoke([HumanMessage(content=prompt)])
            pr = ai.content.strip().lower()
        results.append({"objective": obj, "priority": pr, "status": "READY"})
    return {"tasks": results}
