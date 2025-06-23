from fastapi import FastAPI, HTTPException
from agent import tasks_db

app = FastAPI()


@app.get("/tasks")
def list_tasks():
    return tasks_db.list_tasks()


@app.post("/tasks/{task_id}/approve")
def approve_task(task_id: str):
    task = tasks_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task["status"] = "IN_PROGRESS"
    tasks_db.update_task(task)
    return {"status": "ok"}


@app.post("/tasks/{task_id}/cancel")
def cancel_task(task_id: str):
    task = tasks_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task["status"] = "CANCELLED"
    tasks_db.update_task(task)
    return {"status": "ok"}
