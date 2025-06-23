# Architecture Overview

At a glance, the system is composed of four pillars:

1. **Ingestion** – offline loaders parse files and emails into Qdrant and the Personal Knowledge Graph.
2. **LangGraph agent** – orchestrates planning, retrieval and tool execution.
3. **Vector & Graph stores** – Qdrant and Neo4j provide hybrid memory.
4. **Observability** – Langfuse captures traces for every node and tool.

The full Mermaid diagram is generated from the source code and lives in `architecture/langgraph_flow.md`.
