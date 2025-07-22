import os, sys, importlib
import sqlite3
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from agent import tasks_db

# import the module after path tweaks
api = importlib.import_module("src.task_api")


def setup_temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "tasks.db"
    monkeypatch.setattr(tasks_db, "DB_PATH", str(db_path))
    monkeypatch.setattr(tasks_db, "COLLECTION", "test")
    monkeypatch.setattr(tasks_db, "Qdrant", lambda client, collection_name, embeddings: MagicMock())
    monkeypatch.setattr(tasks_db, "QdrantClient", lambda url: MagicMock())
    def init_custom():
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE tasks (task_id TEXT PRIMARY KEY, data TEXT, updated_at TEXT)")
        conn.commit()
        conn.close()

    monkeypatch.setattr(tasks_db, "init_db", init_custom)
    tasks_db.init_db()
    return db_path


def test_list_tasks(tmp_path, monkeypatch):
    setup_temp_db(tmp_path, monkeypatch)
    tasks_db.add_task({"task_id": "1", "objective": "demo", "status": "NEW"})
    client = TestClient(api.app)
    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert resp.json()[0]["task_id"] == "1"


def test_approve_and_cancel(tmp_path, monkeypatch):
    setup_temp_db(tmp_path, monkeypatch)
    task = {"task_id": "2", "objective": "demo", "status": "WAITING_HITL"}
    tasks_db.add_task(task)
    client = TestClient(api.app)
    resp = client.post("/tasks/2/approve")
    assert resp.status_code == 200
    updated = tasks_db.get_task("2")
    assert updated["status"] == "IN_PROGRESS"
    resp = client.post("/tasks/2/cancel")
    assert resp.status_code == 200
    updated = tasks_db.get_task("2")
    assert updated["status"] == "CANCELLED"


def test_list_tasks_filtered(tmp_path, monkeypatch):
    setup_temp_db(tmp_path, monkeypatch)
    tasks_db.add_task({"task_id": "1", "objective": "demo", "status": "NEW", "priority": "low"})
    tasks_db.add_task({"task_id": "2", "objective": "demo2", "status": "DONE", "priority": "high"})
    client = TestClient(api.app)
    resp = client.get("/tasks", params={"status": "DONE"})
    assert resp.status_code == 200
    assert [t["task_id"] for t in resp.json()] == ["2"]

    resp = client.get("/tasks", params={"priority": "low"})
    assert resp.status_code == 200
    assert [t["task_id"] for t in resp.json()] == ["1"]
