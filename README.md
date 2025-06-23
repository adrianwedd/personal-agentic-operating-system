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

## Graph-Based Planning & Task Management
The planner now incorporates results from the Personal Knowledge Graph. Ambiguous
requests are clarified and tasks are prioritized automatically.

Example:

```bash
python -m tool_agent "Email Jane"
```

If the PKG contains Jane's address, the plan will generate
`draft_email(to='jane.d@example.com')`. Incoming emails matching rules in
`rules/priority.yml` will be elevated without calling the LLM.

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
6. **Sprint 5 – Graph Planning & Task Rules**
   - Verify `plan_step` queries the PKG to expand requests like "Email Jane" into concrete tool calls.
   - Send yourself an email with subject "Invoice" and ensure the `prioritise` node marks it `med` priority without an LLM call.
7. **Sprint 6 – HITL & Meta-Agent**
   - Run the graph in `agent/graph.py` and ensure a task with `requires_hitl` writes a file under `data/hitl_queue/`.
   - Execute `make hitl` to approve the task and check a reflection entry is added in `data/reflections/`.
   - Run `python -m agent.meta_agent` and verify `guidelines.txt` is updated.

