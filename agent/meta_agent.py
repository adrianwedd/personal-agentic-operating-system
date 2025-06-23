"""Meta-agent that synthesizes guidelines from reflection logs."""

from __future__ import annotations

from agent.llm_providers import get_default_client
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient


COLLECTION = "reflections_log"
GUIDELINES_FILE = "guidelines.txt"


def _load_reflections() -> list[str]:
    client = QdrantClient(url="http://localhost:6333")
    store = Qdrant(
        client=client,
        collection_name=COLLECTION,
        embeddings=OllamaEmbeddings(),
    )
    docs = store.similarity_search("recent reflections", k=20)
    return [d.page_content for d in docs]


def run_meta_agent() -> str | None:
    texts = _load_reflections()
    if not texts:
        return None
    llm = get_default_client()
    ai: AIMessage = llm.chat([HumanMessage(content="\n".join(texts))])
    with open(GUIDELINES_FILE, "w") as fh:
        fh.write(ai.content.strip())
    return ai.content.strip()


if __name__ == "__main__":
    run_meta_agent()
