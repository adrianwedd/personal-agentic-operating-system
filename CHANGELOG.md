# Changelog

## v0.4.0
- Added Neo4j container to `docker-compose.yml`.
- Introduced token overflow guard to trim message history.
- Implemented dynamic embedding pipeline for ingestion.
- Added basic tests and coverage fixtures.
- Introduced `scripts/migrate_qdrant_0.4.0.py` to create a payload index on
  the `entities` metadata field.

