"""Simple sqlite task storage and embedding into Qdrant."""
from __future__ import annotations

import json
import os
import sqlite3
from typing import Dict, Any

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

DB_PATH = "data/tasks.db"
COLLECTION = "task_snippets"


def init_db() -> None:
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            data TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


def add_task(task: Dict[str, Any]) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO tasks (task_id, data, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
        (task["task_id"], json.dumps(task)),
    )
    conn.commit()
    conn.close()

    client = QdrantClient(url="http://localhost:6333")
    vs = Qdrant(client=client, collection_name=COLLECTION, embeddings=OllamaEmbeddings())
    vs.add_texts([task["objective"]], ids=[task["task_id"]])


def _qdrant_delete(task_id: str):
    client = QdrantClient(url="http://localhost:6333")
    client.delete(
        collection_name=COLLECTION,
        filter={"must": [{"key": "task_id", "match": {"value": task_id}}]},
    )


def delete_task(task_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM tasks WHERE task_id=?", (task_id,))
    conn.commit()
    conn.close()
    _qdrant_delete(task_id)


def update_task(task: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        UPDATE tasks SET data = ?, updated_at = CURRENT_TIMESTAMP
        WHERE task_id = ?
        """,
        (json.dumps(task), task["task_id"]),
    )
    conn.commit()
    conn.close()
    _qdrant_delete(task["task_id"])
    client = QdrantClient(url="http://localhost:6333")
    vs = Qdrant(client=client, collection_name=COLLECTION, embeddings=OllamaEmbeddings())
    vs.add_texts([task["objective"]], ids=[task["task_id"]])


def get_task(task_id: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT data FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None


def list_tasks() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT data FROM tasks").fetchall()
    conn.close()
    return [json.loads(r[0]) for r in rows]
