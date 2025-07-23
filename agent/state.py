from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage


@dataclass
class AgentState:
    """Shared agent state for LangGraph."""

    messages: List[BaseMessage] = field(default_factory=list)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    current_task: Optional[Dict[str, Any]] = None
    tool_output: Optional[str] = None
    context_docs: List[str] = field(default_factory=list)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def update(self, other: Dict[str, Any]) -> None:
        for k, v in other.items():
            setattr(self, k, v)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
