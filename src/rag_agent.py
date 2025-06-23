from __future__ import annotations

"""Simple RAG agent with hybrid Qdrant retrieval."""

import os
from typing import List, TypedDict, Dict

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from agent.llm_providers import get_default_client
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langfuse.langchain import CallbackHandler
from langfuse import Langfuse
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    """State object for the RAG agent."""

    messages: List[BaseMessage]
    context_docs: List[str]


# --- Retrieval -----------------------------------------------------------------

def _build_retriever() -> any:
    """Create a Qdrant hybrid retriever."""
    client = QdrantClient(url=os.environ.get("QDRANT_URL", "http://localhost:6333"))
    vectorstore = Qdrant(
        client=client,
        collection_name="ingestion",
        embeddings=OllamaEmbeddings(),
    )
    return vectorstore.as_retriever()


retriever = _build_retriever()


def retrieve_context(state: AgentState) -> Dict[str, List[str]]:
    """Fetch relevant documents using the global retriever."""
    query = state["messages"][-1].content
    docs: List[Document] = retriever.invoke(query)
    return {"context_docs": [d.page_content for d in docs]}


# --- LLM -----------------------------------------------------------------------

def answer_step(state: AgentState) -> Dict[str, List[BaseMessage]]:
    """Generate a final answer from context docs and user message."""
    llm = get_default_client()
    prompt = state["messages"][-1].content
    if state.get("context_docs"):
        context = "\n".join(state["context_docs"])
        prompt = f"Context:\n{context}\n---\n{prompt}"
    ai: AIMessage = llm.chat([HumanMessage(content=prompt)])
    return {"messages": state["messages"] + [ai]}


# --- Graph ---------------------------------------------------------------------

def build_graph() -> any:
    """Compile the LangGraph graph for the agent."""
    graph = StateGraph(AgentState)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("answer", answer_step)
    graph.set_entry_point("retrieve_context")
    graph.add_edge("retrieve_context", "answer")
    graph.add_edge("answer", END)
    compiled = graph.compile()
    compiled.get_graph().draw_mermaid_png(output_file_path="rag_graph.png")
    return compiled


compiled_graph = build_graph()


def main(question: str) -> None:
    """Run the agent in CLI mode."""
    state: AgentState = {"messages": [HumanMessage(content=question)], "context_docs": []}
    langfuse = Langfuse()
    handler = CallbackHandler(langfuse)
    result = compiled_graph.invoke(state, config={"callbacks": [handler]})
    final: AIMessage = result["messages"][-1]
    print(final.content)


if __name__ == "__main__":
    import sys

    main(" ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What do I know?")
