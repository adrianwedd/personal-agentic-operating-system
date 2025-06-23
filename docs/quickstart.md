# Quick-start

Clone the repo and launch the development stack:

```bash
git clone https://github.com/adrianwedd/personal-agentic-operating-system.git
cd personal-agentic-operating-system
cp .env.example .env  # fill in secrets
# Langfuse v3+ requires ClickHouse settings:
# CLICKHOUSE_MIGRATION_URL=clickhouse://clickhouse:9000
# CLICKHOUSE_URL=http://clickhouse:8123
# CLICKHOUSE_USER=clickhouse
# CLICKHOUSE_PASSWORD=""
make dev
```

Once services are running, try a simple task:

```bash
python src/minimal_agent.py "Summarise my inbox"
```

The first run downloads an Ollama model (~3 GB). Subsequent runs are fast.

## Switching LLM providers

Set `LLM_BACKEND` in your `.env` file to `openai`, `gemini`, or `deepseek` if you want to use a cloud provider instead of the default Ollama instance. Make sure to also set the matching API key (`OPENAI_API_KEY`, `GEMINI_API_KEY`, or `DEEPSEEK_API_KEY`).
