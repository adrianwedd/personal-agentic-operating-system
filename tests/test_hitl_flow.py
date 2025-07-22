import os, sys, json
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


def test_watch_queue_detects_new(tmp_path, monkeypatch, capsys):
    queue_dir = tmp_path / "queue"
    monkeypatch.setattr("hitl_cli.QUEUE_DIR", str(queue_dir))
    queue_dir.mkdir()
    hitl_cli.watch_queue(interval=0.01, loops=1)
    captured = capsys.readouterr()
    assert "Watching" in captured.out

    with open(queue_dir / "42.json", "w") as fh:
        json.dump({"current_task": {"task_id": "42", "objective": "demo"}}, fh)
    hitl_cli.watch_queue(interval=0.01, loops=1)
    captured = capsys.readouterr()
    assert "42" in captured.out

