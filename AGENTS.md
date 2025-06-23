Of course. Here is the `AGENTS.md` file, created to provide clear and actionable guidelines for AI agents working on this repository. It outlines the project's architecture, defines agent roles, and establishes best practices to ensure efficient and consistent development.

-----

# AGENTS.MD: A Guide for AI Contributors

Welcome, agent. This document is your primary guide for contributing to this repository. Its purpose is to align your work with the project's core architecture, principles, and long-term vision. Adherence to these guidelines is critical for maintaining a clean, modular, and effective codebase.

## 1. Core Philosophy and Architecture

This project aims to build a personal, on-premise agentic operating system. The guiding principle is **"know thyself"**—the agent must be a deep reflection of its user. To achieve this, we follow a specific architectural pattern:

  * **On-Premise First:** All core components (LLM, databases, observability) run locally via Docker to ensure privacy and control.
  * **Modularity:** The system is broken down into distinct services. The core logic is orchestrated by **LangGraph**, which provides granular control over the agent's state and execution flow. [1, 2, 3]
  * **Separation of Concerns:** We distinguish between planning ("what to do") and execution ("how to do it"). A dedicated planner node decomposes tasks, which are then executed by specialized tool-using or retrieval nodes.
  * **Structured Context:** Raw data is not enough. The system is designed to transform unstructured data (emails, files) into structured, actionable context through a **Personal Knowledge Graph (PKG)** and a **Vector Store**. [4, 5]


## Agentic System Execution Lifecycle

The full reasoning loop follows these stages:
1. **Ingest** external data via `ingestion/ingest.py`.
2. **Extract & Embed** context into Qdrant and the PKG.
3. **Accept User Prompt** and start the LangGraph run.
4. **Plan** the request into tasks.
5. **Act** by retrieving context and executing tools per task.
6. **Respond** to the user, optionally passing through HITL.
7. **Reflect** with the meta-agent and update `guidelines.txt`.


### Recommended Repo Structure (partial)

```
.
├── agent/
│   ├── graph.py
│   ├── state.py
│   ├── nodes.py
│   ├── tools.py
│   └── meta_agent.py
├── ingestion/
│   ├── ingest.py
│   ├── loaders.py
│   └── build_pkg.py
├── docker-compose.yml
├── .env
├── requirements.txt  # or pyproject.toml
└── AGENTS.md
```

## 2. Agent Personas & Responsibilities

To streamline development, conceptualize your tasks based on the following agent personas. When you receive a task, identify which persona is best suited to execute it.

### **Architect Agent**

  * **Focus:** System-level infrastructure and service orchestration.
  * **Key Files:** `docker-compose.yml`, environment configuration (`.env`).
  * **Responsibilities:**
      * Define and manage the services in `docker-compose.yml`: `ollama`, `qdrant`, and `langfuse`.
      * Ensure persistent data volumes are correctly configured for Ollama models, Qdrant collections, and Langfuse data.
      * Expose the correct ports for each service (`11434` for Ollama, `6333` for Qdrant, `3000` for Langfuse).
      * Implement the **"Langfuse-first, LangSmith-ready"** strategy. The system must use Langfuse for MVP-stage observability but be architected to switch to a self-hosted LangSmith instance with minimal friction if required in the future. [6, 7, 8]

### **Ingestion Agent**

  * **Focus:** Data loading, processing, and storage into the system's memory stores.
  * **Key Files:** `ingestion/ingest.py`, `ingestion/loaders.py`.
  * **Responsibilities:**
      * Implement data loading using LangChain's `DocumentLoaders`. Primarily use `langchain_google_community.GMailLoader` and `FileSystemLoader`. [9, 10, 11]
      * **Crucially, the ingestion process must be a separate, offline script**, not part of the main agent's real-time loop.
      * Follow the standard ingestion pipeline:
        1.  **Load:** Fetch raw documents from sources.
        2.  **Split:** Use `RecursiveCharacterTextSplitter` to break documents into semantically coherent chunks.
        3.  **Embed:** Generate vector embeddings for each chunk using a model served by the local **Ollama** instance.
        4.  **Store:** Save the text, embeddings, and metadata to the **Qdrant** vector store.

### **Graph Agent (The Brain)**

  * **Focus:** The core reasoning and orchestration logic within LangGraph.
  * **Key Files:** `agent/graph.py`, `agent/state.py`, `agent/nodes.py`.
  * **Responsibilities:**
      * **State Definition:** Define and manage the `AgentState` using Python's `TypedDict`. The state is the single source of truth and must contain fields for `messages`, `tasks`, `current_task`, `tool_output`, and `context_docs`.
      * **Node Implementation:** Implement the core functions as distinct nodes:
          * `plan_step`: Decomposes a user request into a structured list of tasks.
          * `retrieve_context`: Fetches information from Qdrant using hybrid search.
          * `execute_tool`: Calls external tools (e.g., Gmail, Calendar).
          * `generate_response`: Synthesizes a final answer for the user.
      * **Conditional Edges:** Implement the graph's control flow using conditional edges. This is the primary mechanism for decision-making (e.g., deciding whether to retrieve context or execute a tool based on the current task). The graph must support cycles to allow for complex, multi-step reasoning. [6, 2, 12]
      * **Visualization:** Always generate and save a Mermaid diagram of the graph (`graph.get_graph().draw_mermaid_png()`) to aid in debugging and understanding the flow. [6, 12]

### **Tooling Agent**

  * **Focus:** Integrating and managing external tools.
  * **Key Files:** `agent/tools.py`.
  * **Responsibilities:**
      * Integrate pre-built LangChain toolkits, specifically `GmailToolkit` and `GoogleCalendarToolkit`. [13, 14]
      * Ensure correct Google API OAuth scopes are requested. Differentiate between read-only scopes (for ingestion) and write scopes (for creating drafts or calendar events). [13, 14]
      * Use the `ToolNode` from `langgraph.prebuilt` to execute tools within the graph. The planner node should generate the appropriate `tool_calls` for the `ToolNode` to consume. [2]

### **Knowledge Agent**

  * **Focus:** Building and utilizing the Personal Knowledge Graph (PKG).
  * **Key Files:** `ingestion/build_pkg.py`, modifications to `agent/nodes.py`.
  * **Responsibilities:**
      * Implement a batch process using `langchain_experimental.graph_transformers.LLMGraphTransformer` to extract entities and relationships from ingested documents. [4]
      * Constrain the `LLMGraphTransformer` to a predefined schema of allowed node types (e.g., `Person`, `Company`, `Project`) and relationship types to maintain graph consistency. [4]
      * Store the resulting graph triples in a dedicated graph database (e.g., Neo4j, FalkorDB). [4, 15]
      * Upgrade the `retrieve_context` node to perform an advanced, two-step RAG:
        1.  First, query the PKG to identify relevant entities and document IDs.
        2.  Then, perform a targeted vector search in Qdrant using the results from the graph query.

### **Refinement Agent**

  * **Focus:** Implementing the agent's self-improvement and human-in-the-loop capabilities.
  * **Key Files:** `agent/graph.py` (new nodes/edges), `agent/meta_agent.py`.
  * **Responsibilities:**
      * Add a **Human-in-the-Loop (HITL)** checkpoint to the graph for sensitive actions. Use LangGraph's built-in support for interrupting execution and awaiting user input. [2, 3, 16]
      * Log the outcomes of HITL interactions (approvals, rejections, edits) as "reflection" documents into a dedicated Qdrant collection.
      * Create a separate "meta-agent" graph that runs periodically. This agent's purpose is to analyze the reflection logs, synthesize high-level "guidelines" for improvement, and update a central `guidelines.txt` file.
      * Ensure the primary agent's system prompt is dynamically updated with the contents of `guidelines.txt` at runtime, thus closing the learning loop.
The meta-agent embodies the system's capacity for self-awareness. By analyzing reflection logs and rewriting `guidelines.txt`, it allows the agent to refine its own guiding heuristics over time.


## 3. General Contribution Guidelines

  * **Observability is Mandatory:** Every graph invocation (`.invoke()`, `.stream()`) **must** include the `Langfuse` callback handler in its `config`. This is non-negotiable for debugging.
    ```python
    from langfuse.langchain import CallbackHandler

    langfuse_handler = CallbackHandler()
    #...
    response = agent_graph.invoke(
        {"messages": [("user", "some input")]},
        config={"callbacks": [langfuse_handler]}
    )
    ```
  * **State is Sacred:** Nodes must be pure functions. They receive the current state, perform their logic, and return a dictionary containing only the fields they wish to update. Never modify the state object directly.
  * **Local LLM Interaction:** All interactions with the Large Language Model must be routed through the local Ollama instance via the `ChatOllama` LangChain integration. Do not hard-code calls to external APIs. [17, 18]
  * **Dependencies:** All Python dependencies are managed via `pyproject.toml` and `uv` (or a `requirements.txt` file). Do not use global pip installs. Core dependencies include `langgraph`, `langchain`, `langchain-google-community`, `qdrant-client`, `ollama`, and `langfuse`.
  * **Unit Tests Encouraged:** For each node in `agent/nodes.py`, create tests in `tests/test_nodes.py` that mock the state and verify returned fields.
  * **Sanitize Tool Prompts:** When using `ToolNode`, ensure sensitive fields like OAuth tokens are never serialized. Always test tool calls in dry-run mode before production.

