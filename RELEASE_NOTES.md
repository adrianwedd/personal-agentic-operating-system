# Release Notes for v0.4.0

This release introduces a seeded Neo4j service and improves reliability with a token overflow guard. Ingestion now adapts chunking strategy based on document size. Run `make dev` and update your `.env` with `NEO4J_PASSWORD` before starting services.
The `migrate_qdrant_0.4.0.py` script adds an index on the `entities` field to speed up PKG-aware retrieval. Run it once after upgrading.

