# HITL Workflow

Certain tasks require approval before tools execute. When the planner marks a task `requires_hitl`, the graph pauses and writes a JSON file to `data/hitl_queue/`.

Run `make hitl` (or `python src/hitl_cli.py`) to manage pending tasks.
Use `approve` or `reject` to process the next item:

```bash
$ python src/hitl_cli.py approve   # approve first pending task
$ python src/hitl_cli.py reject    # reject first pending task
```
Without arguments the command lists all queued items.
