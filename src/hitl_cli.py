"""CLI for processing HITL queue and logging reflections."""

from __future__ import annotations

import argparse
import glob
import json
import os
import time
from datetime import datetime

import portalocker
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

QUEUE_DIR = "data/hitl_queue"
REFLECT_DIR = "logs"
COLLECTION = "reflections_log"
TTL = 24 * 3600  # 1 day


def _queue_path(task_id: str) -> str:
    return f"{QUEUE_DIR}/{task_id}.json"


def write_hitl(task: dict) -> None:
    os.makedirs(QUEUE_DIR, exist_ok=True)
    with portalocker.Lock(_queue_path(task["task_id"]), "w", timeout=1) as f:
        json.dump(task, f)


def cleanup() -> None:
    now = time.time()
    for fp in glob.glob(f"{QUEUE_DIR}/*.json"):
        if now - os.path.getmtime(fp) > TTL:
            os.remove(fp)


def process_queue(action: str = "approved") -> None:
    os.makedirs(REFLECT_DIR, exist_ok=True)
    files = glob.glob(os.path.join(QUEUE_DIR, "*.json"))
    if not files:
        print("No pending items")
        return
    path = files[0]
    with open(path) as fh:
        state = json.load(fh)
    task = state.get("current_task", {})
    log_path = os.path.join(REFLECT_DIR, "hitl_log.jsonl")
    with open(log_path, "a") as fh:
        fh.write(
            json.dumps({"task_id": task.get("task_id"), "result": action, "ts": datetime.utcnow().isoformat()})
            + "\n"
        )
    client = QdrantClient(url="http://localhost:6333")
    store = Qdrant(client=client, collection_name=COLLECTION, embeddings=OllamaEmbeddings())
    store.add_texts(
        [json.dumps({"task_id": task.get("task_id"), "result": action})],
        ids=[task.get("task_id", "")],
    )
    os.remove(path)
    print(f"Task {task.get('task_id')} {action}")


def list_queue() -> None:
    """Print pending HITL items."""
    files = glob.glob(os.path.join(QUEUE_DIR, "*.json"))
    if not files:
        print("No pending items")
        return
    for fp in files:
        with open(fp) as fh:
            state = json.load(fh)
        task = state.get("current_task", {})
        print(f"{task.get('task_id')}: {task.get('objective', 'no objective')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Process HITL queue")
    parser.add_argument(
        "command",
        choices=["list", "approve", "reject"],
        nargs="?",
        default="list",
        help="Action to perform",
    )
    args = parser.parse_args()

    if args.command == "list":
        list_queue()
    else:
        process_queue(action="approved" if args.command == "approve" else "rejected")


if __name__ == "__main__":
    main()
