"""Agent nodes with PKG-aware planning and retrieval."""

from __future__ import annotations

from typing import List, Dict, Any

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from agent.llm_providers import get_default_client
import os
import re
import yaml
import uuid
from datetime import datetime

from .state import AgentState
from .tasks_db import add_task
from langgraph.prebuilt import ToolNode
from . import tools as agent_tools
from utils.token_counter import trim_messages, count_message_tokens
from .retrieve_context import query_pkg, filter_qdrant_by_entities

tool_node = ToolNode(agent_tools.build_action_tools())


def remaining_steps(task: dict) -> bool:
    return bool(task.get("subtasks"))


GUIDELINES_FILE = "guidelines.txt"


def _load_guidelines() -> str:
    if not os.path.exists(GUIDELINES_FILE):
        return ""
    with open(GUIDELINES_FILE) as fh:
        return fh.read().strip()




# --- Nodes --------------------------------------------------------------------


def retrieve_context(state: AgentState) -> Dict[str, Any]:
    """Retrieve docs using PKG guidance and return metadata."""
    query = state["messages"][-1].content
    _, meta = query_pkg(query)
    entities = [m["entity"] for m in meta if "entity" in m]
    docs, rmeta = filter_qdrant_by_entities(query, entities)
    return {
        "context_docs": [d.page_content for d in docs],
        "graph_metadata": meta,
        "retrieval_meta": rmeta,
    }


def plan_step(state: AgentState) -> Dict[str, Any]:
    """Generate a task list informed by PKG context."""
    prompt = state["messages"][-1].content
    _, meta = query_pkg(prompt)
    parts = []
    for m in meta:
        if "email" in m:
            parts.append(f"{m['entity']} <{m['email']}>")
        else:
            parts.append(m["entity"])
    context = ", ".join(parts)
    llm = get_default_client()
    user_prompt = (
        f"Known entities: {context}\nUser request: {prompt}\nPlan as bullet list."
    )
    guidelines = _load_guidelines()
    messages: List[BaseMessage] = []
    if guidelines:
        messages.append(SystemMessage(content=guidelines))
    messages.append(HumanMessage(content=user_prompt))
    before = count_message_tokens(messages)
    trimmed = trim_messages(messages)
    after = count_message_tokens(trimmed)
    meta_info = {"trimmed": True, "token_delta": before - after} if after < before else {}
    ai: AIMessage = llm.chat(trimmed, metadata=meta_info)
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


def _score_with_llm(llm, objective: str) -> float:
    """Return a numeric urgency score using the LLM (0-1)."""
    prompt = (
        "On a scale from 0 to 1, how urgent is the following task?"
        " Respond with just the number.\nTask: "
        + objective
    )
    msgs = trim_messages([HumanMessage(content=prompt)])
    ai: AIMessage = llm.chat(msgs)
    match = re.search(r"0(?:\.\d+)?|1(?:\.0+)?", ai.content)
    try:
        return float(match.group()) if match else 0.0
    except Exception:
        return 0.0


def _priority_from_score(score: float, rules: dict) -> str:
    """Map numeric score to priority level via thresholds."""
    t = rules.get("llm_thresholds", {})
    if score >= t.get("critical", 0.95):
        return "critical"
    if score >= t.get("high", 0.75):
        return "high"
    if score >= t.get("med", 0.5):
        return "med"
    return rules.get("default", "low")


def prioritise(state: AgentState) -> Dict[str, Any]:
    """Assign priority using deterministic rules then LLM."""
    rules = load_priority_rules()
    llm = get_default_client()

    if state.get("current_task"):
        task = state["current_task"]
        obj = task.get("objective", "")
        sender = task.get("sender")
        pr_det = apply_deterministic_rules(obj, sender, rules)
        score = _score_with_llm(llm, obj)
        pr_llm = _priority_from_score(score, rules)
        if pr_det is None:
            pr = pr_llm
        else:
            order = {"low": 1, "med": 2, "high": 3, "critical": 4}
            pr = pr_det if order.get(pr_det, 0) >= order.get(pr_llm, 0) else pr_llm
        task["priority"] = pr
        task["status"] = "READY"
        add_task(task)
        return {"current_task": task}

    tasks = state.get("tasks", [])
    results = []
    for t in tasks:
        if isinstance(t, dict):
            obj = t.get("objective", "")
            sender = t.get("sender")
        else:
            obj = t
            sender = None
        pr_det = apply_deterministic_rules(obj, sender, rules)
        score = _score_with_llm(llm, obj)
        pr_llm = _priority_from_score(score, rules)
        if pr_det is None:
            pr = pr_llm
        else:
            order = {"low": 1, "med": 2, "high": 3, "critical": 4}
            pr = pr_det if order.get(pr_det, 0) >= order.get(pr_llm, 0) else pr_llm
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
    """Execute the chosen tool and handle errors."""
    task = state["current_task"]
    try:
        tool_calls = task.get("tool_calls", [])
        before = count_message_tokens(tool_calls) if isinstance(tool_calls, list) else 0
        trimmed_calls = trim_messages(tool_calls) if isinstance(tool_calls, list) else tool_calls
        after = count_message_tokens(trimmed_calls) if isinstance(trimmed_calls, list) else 0
        meta_info = {"trimmed": True, "token_delta": before - after} if after < before else {}
        result = tool_node.invoke(trimmed_calls, config={"metadata": meta_info})
        task["tool_output"] = result
        task["status"] = "IN_PROGRESS" if remaining_steps(task) else "DONE"
    except Exception as exc:
        task["status"] = "ERROR"
        task["error"] = str(exc)
    return {"current_task": task}


def generate_response(state: AgentState) -> Dict[str, Any]:
    """Summarize tool output as final message."""
    llm = get_default_client()
    prompt = f"Task {state.get('current_task', {}).get('objective')}: {state.get('tool_output', '')}"
    guidelines = _load_guidelines()
    messages: List[BaseMessage] = []
    if guidelines:
        messages.append(SystemMessage(content=guidelines))
    messages.append(HumanMessage(content=prompt))
    before = count_message_tokens(messages)
    trimmed = trim_messages(messages)
    after = count_message_tokens(trimmed)
    meta_info = {"trimmed": True, "token_delta": before - after} if after < before else {}
    ai: AIMessage = llm.chat(trimmed, metadata=meta_info)
    return {"messages": state.get("messages", []) + [ai], "current_task": None}


def hitl_pause(state: AgentState) -> Dict[str, Any]:
    """Pause execution after an error for HITL."""
    return {}
