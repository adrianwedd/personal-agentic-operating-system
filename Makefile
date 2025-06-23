.PHONY: dev test graph pull-models hitl

dev:
	@echo "Starting services and installing dependencies..."

# run pytest in quiet mode
test:
	pytest -q

# placeholder for graph visualization
graph:
	@echo "Generating graph diagram..."

# pull models for offline use
pull-models:
	@echo "Pulling models for offline use..."

hitl:
	python -m hitl_cli
