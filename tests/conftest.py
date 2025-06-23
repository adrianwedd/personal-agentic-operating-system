import pytest
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def _mock_clients(monkeypatch):
    dummy = MagicMock()
    monkeypatch.setattr("agent.nodes.GraphDatabase.driver", lambda *a, **k: dummy)
    monkeypatch.setattr("ingestion.build_pkg.GraphDatabase.driver", lambda *a, **k: dummy)
    monkeypatch.setattr("qdrant_client.QdrantClient", lambda *a, **k: dummy)
    yield

