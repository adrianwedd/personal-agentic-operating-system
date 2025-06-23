"""Create payload index on entities metadata.

Run this once after upgrading to v0.4.0. Safe to run multiple times.
"""
from __future__ import annotations

import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import PayloadSchemaType


COLLECTION = os.environ.get("QDRANT_COLLECTION", "ingestion")
URL = os.environ.get("QDRANT_URL", "http://localhost:6333")


def migrate() -> None:
    client = QdrantClient(url=URL)
    info = client.get_collection(COLLECTION)
    schema = info.payload_schema or {}
    if "entities" not in schema:
        client.create_payload_index(
            collection_name=COLLECTION,
            field_name="entities",
            field_type=PayloadSchemaType.KEYWORD,
        )
        print("entities index created")
    else:
        print("entities index already exists")


if __name__ == "__main__":
    migrate()
