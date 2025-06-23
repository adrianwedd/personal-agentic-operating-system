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

## Tool Execution
`tool_agent.py` shows how the agent can take real actions using Gmail and Google Calendar. It uses LangChain's `GmailToolkit` and `CalendarToolkit`.

Run it with:

```bash
python -m tool_agent "Draft a reply to Jane and schedule a meeting tomorrow"
```

## Testing
A suite of unit tests is provided under `tests/`. Run them with:

```bash
make test
```

For manual validation, follow these sprint-specific checks:

1. **Sprint 0 – Environment Setup**
   - `docker compose up` then `docker ps` to confirm all containers are healthy.
   - Verify API access: `curl http://localhost:11434/api/tags` and open the Qdrant and Langfuse UIs in the browser.
   - Run `minimal_agent.py` and check Langfuse for a captured trace.
2. **Sprint 1 – Ingestion Pipeline**
   - On first run of `ingestion/ingest.py`, complete the OAuth flow and ensure `token.json` is created.
   - After ingestion, confirm vectors exist in Qdrant via its dashboard.
3. **Sprint 2 – Memory Core (RAG)**
   - Query `rag_agent.py` with known keywords and semantic questions and verify relevant documents are returned.
   - Inspect Langfuse traces to see the `retrieve_context` node outputs.
4. **Sprint 3 – Action Engine (Tools)**
   - Use `tool_agent.py` to schedule a calendar event and draft an email. Confirm the actions in Google Calendar and Gmail Drafts.
5. **Sprint 4 – Personal Knowledge Graph**
   - Run `ingestion/build_pkg.py` and verify a Langfuse trace was recorded.
   - Inspect Neo4j to confirm `Person`, `Company`, and `Project` nodes exist.
   - Query `rag_agent.py` and check that answers reference these entities.

