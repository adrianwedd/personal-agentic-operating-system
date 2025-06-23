"""LangGraph tying nodes together with HITL checkpoint."""
from __future__ import annotations

import json
import os

from langgraph.graph import StateGraph, END
from langfuse.langchain import CallbackHandler
from langfuse import Langfuse
from langchain_core.messages import HumanMessage, AIMessage

from .state import AgentState
from .nodes import (
    plan_step,
    prioritise,
    retrieve_context,
    execute_tool,
    generate_response,
    hitl_pause,
)


HITL_DIR = "data/hitl_queue"


def human_approval(state: AgentState) -> dict:
    """Serialize state for human approval and pause."""
    os.makedirs(HITL_DIR, exist_ok=True)
    task = state.get("current_task")
    if not task:
        return {}
    path = os.path.join(HITL_DIR, f"{task['task_id']}.json")
    with open(path, "w") as fh:
        json.dump(state, fh)
    return {}


def build_graph() -> any:
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan_step)
    graph.add_node("prioritise", prioritise)
    graph.add_node("retrieve", retrieve_context)
    graph.add_node("execute", execute_tool)
    graph.add_node("hitl", human_approval)
    graph.add_node("pause", hitl_pause)
    graph.add_node("respond", generate_response)

    graph.set_entry_point("plan")
    graph.add_edge("plan", "prioritise")
    graph.add_edge("prioritise", "retrieve")
    graph.add_edge("retrieve", "execute")
    graph.add_conditional_edges(
        "execute",
        lambda s: s.get("current_task", {}).get("status"),
        {
            "WAITING_HITL": "hitl",
            "IN_PROGRESS": "prioritise",
            "DONE": "respond",
            "ERROR": "pause",
        },
    )
    graph.add_edge("hitl", END)
    graph.add_edge("pause", END)
    graph.add_edge("respond", END)

    compiled = graph.compile()
    os.makedirs("docs/architecture", exist_ok=True)
    try:
        compiled.get_graph().draw_mermaid_png("docs/architecture/langgraph_flow.png")
    except Exception:
        open("docs/architecture/langgraph_flow.png", "wb").close()
    return compiled


compiled_graph = build_graph()


def main(prompt: str) -> None:
    state: AgentState = {"messages": [HumanMessage(content=prompt)], "tasks": [], "context_docs": [], "current_task": None}
    langfuse = Langfuse()
    handler = CallbackHandler(langfuse)
    result = compiled_graph.invoke(state, config={"callbacks": [handler]})
    final: AIMessage = result["messages"][-1]
    print(final.content)


if __name__ == "__main__":
    import sys

    main(" ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello")
