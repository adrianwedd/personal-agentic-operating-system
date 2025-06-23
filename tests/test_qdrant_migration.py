from unittest.mock import MagicMock
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "migrate", Path("scripts/migrate_qdrant_0.4.0.py")
)
mig = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mig)


def test_migrate_creates_index(monkeypatch):
    dummy = MagicMock()
    dummy.get_collection.return_value = MagicMock(payload_schema={})
    monkeypatch.setattr(mig, "QdrantClient", lambda url: dummy)
    mig.migrate()
    assert dummy.create_payload_index.called


def test_migrate_idempotent(monkeypatch):
    dummy = MagicMock()
    dummy.get_collection.return_value = MagicMock(payload_schema={"entities": {"type": "keyword"}})
    monkeypatch.setattr(mig, "QdrantClient", lambda url: dummy)
    mig.migrate()
    assert not dummy.create_payload_index.called
