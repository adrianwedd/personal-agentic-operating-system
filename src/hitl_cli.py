"""CLI for processing HITL queue and logging reflections."""

from __future__ import annotations

import glob
import json
import os
from datetime import date
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

HITL_DIR = "data/hitl_queue"
REFLECT_DIR = "data/reflections"
COLLECTION = "reflections_log"


def process_queue(action: str = "approved") -> None:
    os.makedirs(REFLECT_DIR, exist_ok=True)
    files = glob.glob(os.path.join(HITL_DIR, "*.json"))
    if not files:
        print("No pending items")
        return
    path = files[0]
    with open(path) as fh:
        state = json.load(fh)
    task = state.get("current_task", {})
    refl_file = os.path.join(REFLECT_DIR, f"{date.today().isoformat()}.jsonl")
    with open(refl_file, "a") as fh:
        fh.write(json.dumps({"task_id": task.get("task_id"), "result": action}) + "\n")
    client = QdrantClient(url="http://localhost:6333")
    store = Qdrant(
        client=client, collection_name=COLLECTION, embeddings=OllamaEmbeddings()
    )
    store.add_texts(
        [json.dumps({"task_id": task.get("task_id"), "result": action})],
        ids=[task.get("task_id", "")],
    )
    os.remove(path)
    print(f"Task {task.get('task_id')} {action}")


if __name__ == "__main__":
    process_queue()
