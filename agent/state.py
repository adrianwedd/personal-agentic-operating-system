from __future__ import annotations

from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage


class AgentState(TypedDict, total=False):
    """Shared agent state for LangGraph."""

    messages: List[BaseMessage]
    tasks: List[Dict[str, Any]]
    current_task: Dict[str, Any] | None
    tool_output: str | None
    context_docs: List[str]
