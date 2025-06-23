# HITL Workflow

Certain tasks require approval before tools execute. When the planner marks a task `requires_hitl`, the graph pauses and writes a JSON file to `data/hitl_queue/`.

Run `make hitl` to review pending tasks. Approving resumes the graph; rejecting logs a reflection for the meta-agent.
