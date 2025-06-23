from langchain_core.messages import AIMessage
from langchain_core.documents import Document
from unittest.mock import MagicMock
import agent.meta_agent as meta


def test_run_meta_agent_updates_guidelines(tmp_path, monkeypatch):
    monkeypatch.setattr(meta, "GUIDELINES_FILE", str(tmp_path / "guide.txt"))

    class DummyStore:
        def similarity_search(self, query, k=20):
            return [Document(page_content="reflect1")]

    monkeypatch.setattr(meta, "Qdrant", lambda client, collection_name, embeddings: DummyStore())
    monkeypatch.setattr(meta, "QdrantClient", lambda url: None)
    monkeypatch.setattr(meta, "OllamaEmbeddings", lambda: None)

    fake_llm = MagicMock()
    fake_llm.chat.return_value = AIMessage(content="New guideline")
    monkeypatch.setattr(meta, "get_default_client", lambda: fake_llm)

    result = meta.run_meta_agent()
    assert result == "New guideline"
    with open(tmp_path / "guide.txt") as fh:
        assert "New guideline" in fh.read()

