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
        "CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, data TEXT)"
    )
    conn.commit()
    conn.close()


init_db()


def add_task(task: Dict[str, Any]) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO tasks (task_id, data) VALUES (?, ?)",
        (task["task_id"], json.dumps(task)),
    )
    conn.commit()
    conn.close()

    client = QdrantClient(url="http://localhost:6333")
    vs = Qdrant(client=client, collection_name=COLLECTION, embeddings=OllamaEmbeddings())
    vs.add_texts([task["objective"]], ids=[task["task_id"]])
