# Personal Agentic Operating System

This repository contains notes and guides for building an on-premise LangGraph-based agentic OS.

## Docs
- [AGENTS.md](AGENTS.md) – personas and contribution rules
- [DEV_ENV.md](DEV_ENV.md) – development environment setup
- [TASKS.md](TASKS.md) – canonical task model

Use `make dev` to start services and install dependencies. See `DEV_ENV.md` for details.

## Ingestion
The `ingestion` package contains an offline script for loading data into Qdrant. It supports Gmail messages and local files.

Run it with:

```bash
python -m ingestion.ingest --gmail-query "is:inbox" --directory ./docs
```

The script splits documents with `RecursiveCharacterTextSplitter`, generates embeddings via the local Ollama model, and stores them in the `ingestion` collection in Qdrant.

## Retrieval
`rag_agent.py` provides a simple RAG example. It queries the `ingestion` collection using a Qdrant retriever and feeds the results to a local LLM. Run it with:

```bash
python -m rag_agent "What do my docs say?"
```
