dev: ## start Docker stack and install deps
	docker compose up -d --pull always
	uv pip install -r requirements.txt

graph: ## render Mermaid graph
	python -c "from agent.graph import build_graph; build_graph()"

onboard: ## interactive onboarding
	python scripts/onboard.py

smoke: ## headless health-check (CI)
	python scripts/check_env.py
	python scripts/healthcheck.py

test: ruff ## run pytest + coverage
	pytest -q --cov=agent --cov-report=term-missing --cov-fail-under=80

ruff: ## lint with ruff
	ruff check .

.PHONY: dev graph test ruff hitl meta-agent task-api ingest help

hitl: ## run HITL CLI
	python src/hitl_cli.py

meta-agent: ## daily meta-agent run
	python scripts/run_meta_agent.py

task-api: ## launch FastAPI task API
	uvicorn src.task_api:app --reload --port 8001

ingest: ## run ingestion pipeline
	env $(grep -v '^#' .env | xargs) python ingestion/ingest.py

docserve: ## live docs
	mkdocs serve

docbuild: ## build static site
	mkdocs build --strict

.PHONY: docserve docbuild help

help: ## show this help
	@awk 'BEGIN {FS = ":";} /^[-a-zA-Z0-9_]+:.*##/ {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort
