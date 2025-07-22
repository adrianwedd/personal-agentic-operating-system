from __future__ import annotations
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Set


LOG_FILE = Path("logs/trace_events.jsonl")
ROTATE_SIZE = 5 * 1024 * 1024  # 5MB


class EventBroker:
    def __init__(self) -> None:
        self.listeners: Set[asyncio.Queue] = set()

    def register(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self.listeners.add(q)
        return q

    def unregister(self, q: asyncio.Queue) -> None:
        self.listeners.discard(q)

    def emit(self, event: dict) -> None:
        for listener in list(self.listeners):
            listener.put_nowait(event)
        self._write_event(event)

    def _write_event(self, event: dict) -> None:
        path = LOG_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(event, ensure_ascii=False)
        if path.exists() and path.stat().st_size + len(line) + 1 > ROTATE_SIZE:
            ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            rotated = path.with_name(f"{path.stem}_{ts}{path.suffix}")
            path.rename(rotated)
        with open(path, "a") as fh:
            fh.write(line + "\n")


broker = EventBroker()
