import sqlite3
import time
from datetime import datetime
from unittest.mock import MagicMock

def test_tasks_db_crud(tmp_path, monkeypatch):
    from agent import tasks_db

    db_path = tmp_path / "tasks.db"
    monkeypatch.setattr(tasks_db, "DB_PATH", str(db_path))
    monkeypatch.setattr(tasks_db, "COLLECTION", "test")

    class DummyVS:
        def __init__(self):
            self.added = []
        def add_texts(self, texts, ids=None):
            self.added.append((texts, ids))
    dummy_vs = DummyVS()
    monkeypatch.setattr(tasks_db, "Qdrant", lambda client, collection_name, embeddings: dummy_vs)
    dummy_client = MagicMock()
    monkeypatch.setattr(tasks_db, "QdrantClient", lambda url: dummy_client)

    def init_custom_db():
        conn = sqlite3.connect(db_path)
        conn.execute(
            """
            CREATE TABLE tasks (
                task_id TEXT PRIMARY KEY,
                data TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()

    monkeypatch.setattr(tasks_db, "init_db", init_custom_db)

    tasks_db.init_db()
    task = {"task_id": "1", "objective": "do it"}
    tasks_db.add_task(task)
    assert dummy_vs.added[-1][0] == ["do it"]

    conn = sqlite3.connect(db_path)
    ts1 = conn.execute("SELECT updated_at FROM tasks WHERE task_id='1'").fetchone()[0]
    conn.close()
    assert ts1 is not None

    time.sleep(1)

    task["objective"] = "update"
    tasks_db.update_task(task)
    assert len(dummy_vs.added) == 2
    assert dummy_client.delete.call_count == 1

    conn = sqlite3.connect(db_path)
    ts2 = conn.execute("SELECT updated_at FROM tasks WHERE task_id='1'").fetchone()[0]
    conn.close()
    assert datetime.fromisoformat(ts2) > datetime.fromisoformat(ts1)

    tasks_db.delete_task("1")
    assert dummy_client.delete.call_count == 2

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT * FROM tasks WHERE task_id='1'").fetchone()
    conn.close()
    assert row is None


def test_search_tasks_returns_most_similar(tmp_path, monkeypatch):
    from agent import tasks_db

    db_path = tmp_path / "tasks.db"
    monkeypatch.setattr(tasks_db, "DB_PATH", str(db_path))
    monkeypatch.setattr(tasks_db, "COLLECTION", "test")

    class DummyVS:
        def __init__(self):
            self.added = []
            self.results = []

        def add_texts(self, texts, ids=None):
            self.added.append((texts, ids))

        def similarity_search_with_score(self, query, k=5):
            return self.results

    dummy_vs = DummyVS()
    monkeypatch.setattr(tasks_db, "Qdrant", lambda client, collection_name, embeddings: dummy_vs)
    monkeypatch.setattr(tasks_db, "QdrantClient", lambda url: MagicMock())
    monkeypatch.setattr(tasks_db, "OllamaEmbeddings", lambda: None)

    def init_custom_db():
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE tasks (task_id TEXT PRIMARY KEY, data TEXT, updated_at TEXT)"
        )
        conn.commit()
        conn.close()

    monkeypatch.setattr(tasks_db, "init_db", init_custom_db)

    tasks_db.init_db()

    tasks_db.add_task({"task_id": "1", "objective": "buy milk"})
    tasks_db.add_task({"task_id": "2", "objective": "write report"})

    from langchain_core.documents import Document

    dummy_vs.results = [
        (Document(page_content="buy milk", metadata={"_id": "1"}), 0.1),
        (Document(page_content="write report", metadata={"_id": "2"}), 0.2),
    ]

    results = tasks_db.search_tasks("milk")
    assert [t["task_id"] for t in results] == ["1", "2"]
