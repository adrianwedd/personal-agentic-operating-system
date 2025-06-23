dev:
	docker compose up -d --pull always
	uv pip install -r requirements.txt

graph:
	python -c "from agent.graph import build_graph; build_graph()"

onboard:
	python scripts/onboard.py

smoke:                 ## headless health-check (CI)
	python - <<'PY'
	from scripts.healthcheck import wait_for_stack
	import sys
	ok, report = wait_for_stack(timeout=60)
	print(report)
	sys.exit(0 if ok else 1)
	PY

test: ruff
	pytest -q --cov=agent --cov-report=term-missing --cov-fail-under=80

ruff:
	ruff check .

.PHONY: dev graph test ruff hitl meta-agent task-api

hitl:
	python src/hitl_cli.py

meta-agent:
	python scripts/run_meta_agent.py

task-api:
	uvicorn src.task_api:app --reload --port 8001

docserve:  ## live docs
	mkdocs serve

docbuild:  ## build static site
	mkdocs build --strict
.PHONY: docserve docbuild
