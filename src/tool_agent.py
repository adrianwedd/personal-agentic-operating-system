from __future__ import annotations

"""Agent that can draft emails and schedule calendar events."""

from typing import List, Dict, TypedDict

from agent.llm_providers import get_default_client
from langchain_google_community import GmailToolkit, CalendarToolkit
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.prebuilt import create_react_agent


class AgentState(TypedDict):
    """State for the tool agent."""

    messages: List[BaseMessage]
    remaining_steps: int


def build_tools() -> List:
    """Instantiate Gmail and Calendar tools."""
    gmail_tools = GmailToolkit().get_tools()
    cal_tools = CalendarToolkit().get_tools()
    return list(gmail_tools) + list(cal_tools)


def build_agent() -> any:
    """Create the LangGraph agent with tools and save graph diagram."""
    llm = get_default_client()
    tools = build_tools()
    agent = create_react_agent(llm.chat_model if hasattr(llm, "chat_model") else llm, tools)
    agent.get_graph().draw_mermaid_png(output_file_path="tool_graph.png")
    return agent


def main(prompt: str) -> None:
    """Run the tool agent in CLI mode."""
    agent = build_agent()
    state: AgentState = {
        "messages": [HumanMessage(content=prompt)],
        "remaining_steps": 5,
    }
    langfuse = Langfuse()
    handler = CallbackHandler(langfuse)
    result = agent.invoke(state, config={"callbacks": [handler]})
    final: AIMessage = result["messages"][-1]
    print(final.content)


if __name__ == "__main__":
    import sys

    main(" ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello")
