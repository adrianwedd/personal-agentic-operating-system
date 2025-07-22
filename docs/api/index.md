# API Reference

These endpoints expose a very small task management API used by the CLI and
HITL tooling. The server is expected to run locally, so no authentication is
implemented.

## List tasks

`GET /tasks`

Return all tasks known to the system. You can optionally filter by
`status` or `priority` query parameters.

### Example

```bash
curl -X GET "http://localhost:8000/tasks?status=WAITING_HITL"
```

```json
[
  {
    "task_id": "123",
    "objective": "draft update email",
    "status": "WAITING_HITL",
    "priority": "medium"
  }
]
```

---

## Approve task

`POST /tasks/{task_id}/approve`

Mark a pending task as `IN_PROGRESS` so the agent may continue execution.

### Example

```bash
curl -X POST http://localhost:8000/tasks/123/approve
```

```json
{"status": "ok"}
```

---

## Cancel task

`POST /tasks/{task_id}/cancel`

Set the task status to `CANCELLED`.

### Example

```bash
curl -X POST http://localhost:8000/tasks/123/cancel
```

```json
{"status": "ok"}
```

---

### Authentication

None. All routes assume a trusted local environment.

