from typing import TypedDict, List

from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.graph.state import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langfuse import Langfuse, LangfuseCallbackHandler


class AgentState(TypedDict):
    """State for the minimal agent."""

    messages: List[HumanMessage]


def ollama_step(state: AgentState) -> AgentState:
    llm = ChatOllama()
    last = state["messages"][-1]
    response = llm.invoke([last])
    state["messages"].append(response)
    return state


def main(prompt: str) -> None:
    state = {"messages": [HumanMessage(content=prompt)]}
    graph = StateGraph(AgentState)
    graph.add_node("ollama", ollama_step)
    graph.set_entry_point("ollama")
    graph.add_edge("ollama", END)
    compiled = graph.compile()
    langfuse = Langfuse()
    handler = LangfuseCallbackHandler(langfuse)
    result = compiled.invoke(state, config={"callbacks": [handler]})
    final: AIMessage = result["messages"][-1]
    print(final.content)


if __name__ == "__main__":
    import sys

    prompt_arg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello"
    main(prompt_arg)
