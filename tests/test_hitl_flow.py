import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import hitl_cli

def test_hitl_write_and_process(tmp_path, monkeypatch):
    queue_dir = tmp_path / "queue"
    refl_dir = tmp_path / "logs"
    monkeypatch.setattr("hitl_cli.QUEUE_DIR", str(queue_dir))
    monkeypatch.setattr("hitl_cli.REFLECT_DIR", str(refl_dir))

    class DummyStore:
        def __init__(self):
            self.texts = []

        def add_texts(self, texts, ids=None):
            self.texts.extend(texts)

    dummy = DummyStore()
    monkeypatch.setattr(
        "hitl_cli.Qdrant", lambda client, collection_name, embeddings: dummy
    )
    monkeypatch.setattr("hitl_cli.QdrantClient", lambda url: None)
    monkeypatch.setattr("hitl_cli.OllamaEmbeddings", lambda: None)

    hitl_cli.write_hitl({"task_id": "1"})
    assert (queue_dir / "1.json").exists()

    hitl_cli.process_queue(action="approved")
    assert dummy.texts
    assert list(refl_dir.glob("*.jsonl"))

