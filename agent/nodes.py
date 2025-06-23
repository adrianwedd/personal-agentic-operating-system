"""Agent nodes with PKG-aware planning and retrieval."""

from __future__ import annotations

from typing import List, Dict, Any

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from neo4j import GraphDatabase
import os
import re
import yaml
import uuid
from datetime import datetime

from .state import AgentState
from .tasks_db import add_task


GUIDELINES_FILE = "guidelines.txt"


def _load_guidelines() -> str:
    if not os.path.exists(GUIDELINES_FILE):
        return ""
    with open(GUIDELINES_FILE) as fh:
        return fh.read().strip()


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
    guidelines = _load_guidelines()
    messages: List[BaseMessage] = []
    if guidelines:
        messages.append(SystemMessage(content=guidelines))
    messages.append(HumanMessage(content=user_prompt))
    ai: AIMessage = llm.invoke(messages)
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
        results.append(
            {
                "task_id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat() + "Z",
                "objective": obj,
                "priority": pr,
                "status": "READY",
                "subtasks": [],
                "last_updated": datetime.utcnow().isoformat() + "Z",
            }
        )
        add_task(results[-1])
    return {"tasks": results}


def execute_tool(state: AgentState) -> Dict[str, Any]:
    """Fake tool execution with optional HITL."""
    tasks = state.get("tasks", [])
    if not tasks:
        return {}
    task = tasks[0]
    task["status"] = "IN_PROGRESS"
    if task.get("requires_hitl"):
        task["status"] = "WAITING_HITL"
    return {"current_task": task, "tasks": tasks}


def generate_response(state: AgentState) -> Dict[str, Any]:
    """Summarize tool output as final message."""
    llm = ChatOllama()
    prompt = f"Task {state.get('current_task', {}).get('objective')}: {state.get('tool_output', '')}"
    guidelines = _load_guidelines()
    messages: List[BaseMessage] = []
    if guidelines:
        messages.append(SystemMessage(content=guidelines))
    messages.append(HumanMessage(content=prompt))
    ai: AIMessage = llm.invoke(messages)
    return {"messages": state.get("messages", []) + [ai], "current_task": None}
