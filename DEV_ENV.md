# Development Environment Guide

This file provides the minimal, machine-readable facts needed to run and test the project consistently. Agents should consult it before generating any Docker, Python, or CI configuration.

## 1. Runtime Matrix
- `PYTHON_VERSION=3.11`
- Node.js 18+ and Yarn
- Docker Compose v2 or newer
- Works on CPU; optional CUDA acceleration for Ollama

## 2. Core Services
```yaml
services:
  ollama:
    image: ollama/ollama:0.2.0
    ports: ["11434:11434"]
    volumes:
      - ./data/ollama:/root/.ollama
  qdrant:
    image: qdrant/qdrant:v1.9.0
    ports: ["6333:6333"]
    volumes:
      - ./data/qdrant:/qdrant/storage
  langfuse:
    image: ghcr.io/langfuse/langfuse:3.74.0
    ports: ["3000:3000"]
    volumes:
      - ./data/langfuse:/data
    environment:
      DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres/${POSTGRES_DB}
      NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
      SALT: ${SALT}
  neo4j:
    image: neo4j:5.20
    ports: ["7687:7687"]
    environment:
      NEO4J_AUTH: ${NEO4J_AUTH}
    volumes:
      - ./data/neo4j:/data
```

Neo4j loads `constraints.cypher` from `/docker-entrypoint-initdb.d/` on the first
container start to install PKG constraints.

## 3. Environment Variables
Example `.env` values (no secrets):
```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
OLLAMA_MODELS=/data/models
NEO4J_AUTH=neo4j/passw0rd
LANGFUSE_PUBLIC_KEY=changeme
LANGFUSE_SECRET_KEY=changeme
NEXTAUTH_SECRET=0123456789abcdef0123456789abcdef
SALT=fedcba9876543210fedcba9876543210
DATABASE_URL=postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres/${POSTGRES_DB}
```
Copy `.env.example` to `.env` and update values before running `docker compose up`.
The Langfuse image is multi-arch, so no `platform:` override is required on Apple Silicon.
You can also run `./bootstrap.sh` for a guided setup that configures `.env` and pulls the stack images.

## 4. Dev Scripts
Makefile targets expected by agents:
```bash
make dev   # start services and install deps
make test  # run pytest -q
make graph # output Mermaid diagram
```

## 5. Pre-commit & Linting
- `ruff>=0.4` configured via `pyproject.toml`
- `black` for code formatting
- Install hooks with `pre-commit install`

## 6. Recommended IDE
Use VS Code Remote-Containers with `.devcontainer/devcontainer.json` if available.

## 7. Persistence Paths
- `./data/qdrant/`
- `./data/ollama/`
- `./logs/langgraph/`

## ClickHouse for Langfuse v3+

Langfuse v3 and newer relies on ClickHouse. A development‑tuned configuration
is provided at `.clickhouse/config.xml` and keeps system logs compact while
reducing background thread usage. Docker Compose mounts this file automatically
if you ran `bootstrap.sh`.

To enforce a 3‑day TTL on ClickHouse's system logs, run:

```bash
bash scripts/prune_clickhouse_system_tables.sh
```

See `tests/test_clickhouse_dev_defaults.py` for verification of these settings.

## 8. Offline/Air-Gap Notes
Run `make pull-models` before going offline. If using a mirror registry, update `docker-compose.yml` accordingly.

## 9. Test Dataset Stubs
Place small fixture emails and documents under `tests/fixtures/` for unit tests.

## 10. Scheduling the Meta-Agent
Run `python scripts/run_meta_agent.py` daily to refresh `guidelines.txt` from reflection logs.
Add a cron entry or systemd timer that invokes the script once per day.
