from __future__ import annotations
import asyncio
from typing import Any, Set


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


broker = EventBroker()
