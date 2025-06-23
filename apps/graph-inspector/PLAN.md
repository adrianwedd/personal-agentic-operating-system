We are aiming for a complete proof-of-concept showing live LangGraph visualization with real-time event coloring. The goal is a minimal but working FastAPI backend and React-Flow UI.

---

# Graph Inspector PoC Plan

## 1. Spike: FastAPI + React-Flow

Phase | Task | Output
---- | ---- | ----
1.1 | `@event_emitter` decorator or hook emits `NodeStarted` and `NodeFinished` events | Publish to local Redis
1.2 | `trace-agent.py` exposes `GET /graph-events` via SSE or WebSocket | Stream LangGraph node updates
1.3 | Scaffold `apps/graph-inspector/` with React, Tailwind, shadcn, React-Flow | Local dev UI using Vite
1.4 | Mock DAG `A -> B -> C` | Use static `graph.json` or introspect LangGraph
1.5 | Subscribe to live events in React app and color nodes running/finished/error | Real-time visual feedback

---

## 2. Directory structure & integration

```
personal-agentic-operating-system/
├── agent/                           # existing LangGraph logic
├── apps/
│   └── graph-inspector/            # React app (graph UI)
├── trace-agent/                    # FastAPI server w/ event bridge
├── docker-compose.yml              # Add new services: trace-agent, graph-inspector (static)
├── .env                            # Add REDIS_URL, EVENT_STREAM_BACKEND, etc.
└── README.md                       # Document setup + run instructions
```

---

## 3. Local Dev Commands

```
./bootstrap.sh                        # build + run all services

docker compose up --build trace-agent graph-inspector   # manual

yarn dev   # in apps/graph-inspector for hot reload
```

---

## 4. Acceptance Criteria
- Node state changes reflected live
- UI updates via WebSocket or SSE without refresh
- Only decorator/hooks added to LangGraph
- Works via `docker compose up` and auto-wires Redis
- Devs can add their own DAG and see it live

---

## 5. Stretch Goals (not blocking)

Feature | Value
--- | ---
Zoom to subgraphs | Easier UX with large DAGs
View node logs/payloads | Inspect token usage, errors
Snapshot graphs to ClickHouse or PG | Audit trail, comparisons
Load multiple DAGs by run_id | Compare agent runs
Replay graph flow | Education & debugging

---

Commit this file as `apps/graph-inspector/PLAN.md` and evolve it as development proceeds.

---

# LangGraph Inspector PoC Plan (Summary)

This PoC demonstrates a real-time graph inspector using FastAPI and React-Flow.

## Spike Steps

Phase | Task | Output
---- | ---- | ----
1.1 | Implement event emitter hook | emit to Redis
1.2 | FastAPI endpoint `/graph-events` | streaming updates
1.3 | Scaffold React frontend | ready for dev
1.4 | Mock 3-node DAG | static or introspected
1.5 | Visualize node transitions live | color idle/running/finished/error

## Dev Instructions

```
./bootstrap.sh
cd trace-agent && uvicorn main:app --reload
cd apps/graph-inspector && yarn dev
```

## CODEX tasks

- id: GRAPH-001 — Spike a FastAPI server to simulate events.
- id: GRAPH-002 — Set up React-Flow playground under apps/graph-inspector.
- id: GRAPH-003 — Connect FastAPI endpoint to React UI with WebSocket or SSE.
- id: GRAPH-004 — Animate node transitions when events arrive.
- id: GRAPH-005 — Document the PoC and how to run locally.
- id: GRAPH-006 — Define shared event types in Python and TypeScript.
