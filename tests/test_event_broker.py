import json
from pathlib import Path
from unittest.mock import mock_open, MagicMock

import trace_agent.event_broker as eb


def test_emit_writes_json_line(monkeypatch):
    broker = eb.EventBroker()
    m = mock_open()
    monkeypatch.setattr("builtins.open", m)
    path = Path("dummy.jsonl")
    monkeypatch.setattr(eb, "LOG_FILE", path)
    monkeypatch.setattr(Path, "mkdir", lambda self, parents=False, exist_ok=False: None)
    monkeypatch.setattr(Path, "exists", lambda self: False)
    monkeypatch.setattr(Path, "stat", lambda self: type("S", (), {"st_size": 0})())

    broker.emit({"a": 1})

    m.assert_called_once_with(path, "a")
    handle = m()
    handle.write.assert_called_once_with(json.dumps({"a": 1}, ensure_ascii=False) + "\n")


def test_emit_rotates_when_large(monkeypatch):
    broker = eb.EventBroker()
    m = mock_open()
    path = Path("dummy.jsonl")
    monkeypatch.setattr("builtins.open", m)
    monkeypatch.setattr(eb, "LOG_FILE", path)
    monkeypatch.setattr(eb, "ROTATE_SIZE", 10)
    monkeypatch.setattr(Path, "mkdir", lambda self, parents=False, exist_ok=False: None)
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "stat", lambda self: type("S", (), {"st_size": 20})())
    rename_mock = MagicMock()
    monkeypatch.setattr(Path, "rename", lambda self, dst: rename_mock(dst))

    broker.emit({"b": 2})

    assert rename_mock.called
    handle = m()
    handle.write.assert_called_once()
