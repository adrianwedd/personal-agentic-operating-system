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
from trace_agent.decorators import traced


HITL_DIR = "data/hitl_queue"


def human_approval(state: AgentState) -> dict:
    """Serialize state for human approval and pause."""
    os.makedirs(HITL_DIR, exist_ok=True)
    task = state.get("current_task")
    if not task:
        return {}
    path = os.path.join(HITL_DIR, f"{task['task_id']}.json")
    with open(path, "w") as fh:
        json.dump(state.to_dict(), fh)
    return {}


def build_graph() -> any:
    graph = StateGraph(AgentState)
    graph.add_node("plan", traced("plan")(plan_step))
    graph.add_node("prioritise", traced("prioritise")(prioritise))
    graph.add_node("retrieve", traced("retrieve")(retrieve_context))
    graph.add_node("execute", traced("execute")(execute_tool))
    graph.add_node("hitl", traced("hitl")(human_approval))
    graph.add_node("pause", traced("pause")(hitl_pause))
    graph.add_node("respond", traced("respond")(generate_response))

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


def graph_layout() -> dict:
    """Return nodes and edges suitable for ReactFlow."""
    graph = compiled_graph.get_graph()
    nodes = []
    x = 0
    for node in graph.nodes:
        if node in {"__start__", "__end__"}:
            continue
        nodes.append({
            "id": node,
            "position": {"x": x, "y": 0},
            "data": {"label": node},
        })
        x += 150

    edges = []
    for edge in graph.edges:
        if edge.source in {"__start__", "__end__"} or edge.target in {"__start__", "__end__"}:
            continue
        edges.append({
            "id": f"{edge.source}-{edge.target}",
            "source": edge.source,
            "target": edge.target,
        })

    return {"nodes": nodes, "edges": edges}


def main(prompt: str) -> None:
    state = AgentState(
        messages=[HumanMessage(content=prompt)],
        tasks=[],
        context_docs=[],
        current_task=None,
    )
    langfuse = Langfuse()
    handler = CallbackHandler(langfuse)
    result = compiled_graph.invoke(state, config={"callbacks": [handler]})
    final: AIMessage = result["messages"][-1]
    print(final.content)


if __name__ == "__main__":
    import sys

    main(" ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello")
