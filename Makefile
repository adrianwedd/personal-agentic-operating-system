dev:
	docker compose up -d --pull always
	uv pip install -r requirements.txt

graph:
	python -c "from agent.graph import build_graph; build_graph()"

test: ruff
	pytest -q --cov=agent --cov-report=term-missing --cov-fail-under=80

ruff:
	ruff check .


.PHONY: dev graph test ruff hitl meta-agent

hitl:
	python src/hitl_cli.py

meta-agent:
	python scripts/run_meta_agent.py



docserve:  ## live docs
	mkdocs serve

docbuild:  ## build static site
	mkdocs build --strict
.PHONY: docserve docbuild
