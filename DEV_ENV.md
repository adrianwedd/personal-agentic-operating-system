# Development Environment Guide

This file provides the minimal, machine-readable facts needed to run and test the project consistently. Agents should consult it before generating any Docker, Python, or CI configuration.

## 1. Runtime Matrix
- `PYTHON_VERSION=3.11`
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
    image: ghcr.io/langfuse/langfuse:2.3.1
    ports: ["3000:3000"]
    volumes:
      - ./data/langfuse:/data
  neo4j:
    image: neo4j:5.20
    ports: ["7687:7687"]
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
    volumes:
      - ./data/neo4j:/data
```

## 3. Environment Variables
Example `.env` values (no secrets):
```env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
OLLAMA_MODELS=/data/models
NEO4J_PASSWORD=passw0rd
```

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

## 8. Offline/Air-Gap Notes
Run `make pull-models` before going offline. If using a mirror registry, update `docker-compose.yml` accordingly.

## 9. Test Dataset Stubs
Place small fixture emails and documents under `tests/fixtures/` for unit tests.
