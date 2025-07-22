# Testing Strategy

This project ships with a comprehensive pytest suite covering most of the agent modules.
Running `make test` executes `ruff` and `pytest` with coverage enabled.
At the time of writing the suite reports roughly **91%** line coverage.

## Current Coverage Snapshot

```
# excerpt from `pytest --cov` run
agent/llm_providers/__init__.py             15      0   100%
agent/llm_providers/base.py                 14      0   100%
agent/llm_providers/deepseek_client.py      34      2    94%
agent/llm_providers/gemini_client.py        29      3    90%
agent/llm_providers/ollama_client.py        20      1    95%
agent/llm_providers/openai_client.py        23      1    96%
... 
TOTAL                                      516     45    91%
```

Most tests exercise the graph construction, task lifecycle, ingestion pipeline and the OpenAI client. `tests/test_clickhouse_dev_defaults.py` spins up a Docker container to verify the ClickHouse configuration.

## LLM Provider Coverage

Unit tests now cover all LLM providers. The table below summarises the state of coverage:

| Provider      | Module Path                                   | Tests Present? |
|---------------|-----------------------------------------------|----------------|
| **Ollama**    | `agent/llm_providers/ollama_client.py`        | Yes |
| **OpenAI**    | `agent/llm_providers/openai_client.py`        | Yes |
| **Gemini**    | `agent/llm_providers/gemini_client.py`        | Yes |
| **DeepSeek**  | `agent/llm_providers/deepseek_client.py`      | Yes |

## Areas for Improvement

* **LLM Clients** – Maintain mocks for all providers so tests remain offline.
* **Docker Based Tests** – `test_clickhouse_dev_defaults` requires Docker; consider marking it optional or providing a stubbed ClickHouse client when Docker is unavailable.
* **End‑to‑End Runs** – Minimal integration tests exist for meta and tool agents. Expanding scenario coverage will catch regressions in the LangGraph flow.

## Recommended Approach

1. Use `monkeypatch` or libraries like `responses` to stub API calls.
2. Parameterise tests by setting `LLM_BACKEND` to each provider and validating `chat`, `stream_chat` and `embed` behaviour.
3. Ensure coverage thresholds remain above **80%** to comply with CI requirements.
