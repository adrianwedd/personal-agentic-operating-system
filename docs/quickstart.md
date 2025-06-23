# Quick-start

Clone the repo and launch the development stack:

```bash
git clone https://github.com/adrianwedd/personal-agentic-operating-system.git
cd personal-agentic-operating-system
cp .env.example .env  # fill in secrets
make dev
```

Once services are running, try a simple task:

```bash
python src/minimal_agent.py "Summarise my inbox"
```

The first run downloads an Ollama model (~3 GB). Subsequent runs are fast.
