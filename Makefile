dev:
	docker compose up -d --pull always
	uv pip install -r requirements.txt

graph:
	python -c "from agent.graph import build_graph; build_graph()"

test: ruff
	pytest -q --cov=agent --cov-report=term-missing

ruff:
	ruff .

.PHONY: dev graph test ruff



docserve:
	mkdocs serve

docbuild:
	mkdocs build --strict
.PHONY: docserve docbuild
