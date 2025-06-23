from typing import TypedDict, List

from agent.llm_providers import get_default_client
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler


class AgentState(TypedDict):
    """State for the minimal agent."""

    messages: List[HumanMessage]


def ollama_step(state: AgentState) -> dict:
    """Call the local model and return an updated messages list."""
    llm = get_default_client()
    last = state["messages"][-1]
    response = llm.chat([last])
    return {"messages": state["messages"] + [response]}


def main(prompt: str) -> None:
    state = {"messages": [HumanMessage(content=prompt)]}
    graph = StateGraph(AgentState)
    graph.add_node("ollama", ollama_step)
    graph.set_entry_point("ollama")
    graph.add_edge("ollama", END)
    compiled = graph.compile()
    langfuse = Langfuse()
    handler = CallbackHandler(langfuse)
    result = compiled.invoke(state, config={"callbacks": [handler]})
    final: AIMessage = result["messages"][-1]
    print(final.content)


if __name__ == "__main__":
    import sys

    prompt_arg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello"
    main(prompt_arg)
