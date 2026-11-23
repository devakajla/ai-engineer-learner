from enum import Enum
from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Path, Query

app = FastAPI(
    title="TaskFlow",
    version="0.1.0",
    description="A task-manager REST API",
)


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


# Temporary in-memory storage. A real database replaces this in Level 2.
TASKS: list[dict[str, Any]] = [
    {"id": 1, "title": "Set up TaskFlow", "description": None, "priority": "high", "done": True},
    {"id": 2, "title": "Learn path parameters", "description": None, "priority": "medium", "done": False},
    {"id": 3, "title": "Write the README", "description": "Explain how to run the API", "priority": "low", "done": False},
]


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Liveness check used by load balancers and monitoring."""
    return {"status": "ok"}


@app.get("/tasks", tags=["tasks"])
def list_tasks(
    done: bool | None = None,
    priority: Priority | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[dict[str, Any]]:
    tasks = TASKS
    if done is not None:
        tasks = [t for t in tasks if t["done"] == done]
    if priority is not None:
        tasks = [t for t in tasks if t["priority"] == priority.value]
    return tasks[:limit]


@app.get("/tasks/{task_id}", tags=["tasks"])
def get_task(task_id: Annotated[int, Path(ge=1)]) -> dict[str, Any]:
    for task in TASKS:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")
