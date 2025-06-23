# Testing Strategy

This project ships with a comprehensive pytest suite covering most of the agent modules.
Running `make test` executes `ruff` and `pytest` with coverage enabled.
At the time of writing the suite reports roughly **85%** line coverage.

## Current Coverage Snapshot

```
# excerpt from `pytest --cov` run
agent/llm_providers/__init__.py             15      0   100%
agent/llm_providers/base.py                 14      0   100%
agent/llm_providers/deepseek_client.py      34     19    44%
agent/llm_providers/gemini_client.py        29     15    48%
agent/llm_providers/ollama_client.py        20      4    80%
agent/llm_providers/openai_client.py        23      3    87%
...
TOTAL                                      511     78    85%
```

Most tests exercise the graph construction, task lifecycle, ingestion pipeline and the OpenAI client. `tests/test_clickhouse_dev_defaults.py` spins up a Docker container to verify the ClickHouse configuration.

## LLM Provider Coverage

Only the OpenAI backend has dedicated unit tests. Other providers are instantiated indirectly when selected via `LLM_BACKEND`, but their request logic is untested. The table below summarises the state of coverage:

| Provider      | Module Path                                   | Tests Present? |
|---------------|-----------------------------------------------|----------------|
| **Ollama**    | `agent/llm_providers/ollama_client.py`        | No |
| **OpenAI**    | `agent/llm_providers/openai_client.py`        | Yes |
| **Gemini**    | `agent/llm_providers/gemini_client.py`        | No |
| **DeepSeek**  | `agent/llm_providers/deepseek_client.py`      | No |

## Areas for Improvement

* **LLM Clients** – Add unit tests for `OllamaClient`, `GeminiClient` and `DeepSeekClient`. Mock the underlying SDK or HTTP calls so tests remain offline.
* **Docker Based Tests** – `test_clickhouse_dev_defaults` requires Docker; consider marking it optional or providing a stubbed ClickHouse client when Docker is unavailable.
* **End‑to‑End Runs** – Minimal integration tests exist for meta and tool agents. Expanding scenario coverage will catch regressions in the LangGraph flow.

## Recommended Approach

1. Use `monkeypatch` or libraries like `responses` to stub API calls.
2. Parameterise tests by setting `LLM_BACKEND` to each provider and validating `chat`, `stream_chat` and `embed` behaviour.
3. Ensure coverage thresholds remain above **80%** to comply with CI requirements.
