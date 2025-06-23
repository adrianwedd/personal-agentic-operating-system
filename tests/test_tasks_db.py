import sqlite3
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
            "CREATE TABLE tasks (task_id TEXT PRIMARY KEY, data TEXT, updated_at TEXT)"
        )
        conn.commit()
        conn.close()

    monkeypatch.setattr(tasks_db, "init_db", init_custom_db)

    tasks_db.init_db()
    task = {"task_id": "1", "objective": "do it"}
    tasks_db.add_task(task)
    assert dummy_vs.added[-1][0] == ["do it"]

    task["objective"] = "update"
    tasks_db.update_task(task)
    assert len(dummy_vs.added) == 2
    assert dummy_client.delete.call_count == 1

    tasks_db.delete_task("1")
    assert dummy_client.delete.call_count == 2

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT * FROM tasks WHERE task_id='1'").fetchone()
    conn.close()
    assert row is None
