
dev:                   ## spin up stack + install deps
	docker compose up -d --pull always
	uv pip install -r requirements.txt

graph:                 ## render graph PNG
	python - <<'PY'
	from agent.graph import graph
	graph.get_graph().draw_mermaid_png("docs/langgraph.png")
	PY

test: ruff             ## lint + tests + coverage
	pytest -q --cov=agent --cov-report=term-missing

ruff:
	ruff .

.PHONY: dev graph test ruff
