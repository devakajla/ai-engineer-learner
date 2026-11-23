from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Path, Query, status

from app.schemas.task import Priority, TaskCreate, TaskRead, TaskUpdate

app = FastAPI(
    title="TaskFlow",
    version="0.1.0",
    description="A task-manager REST API",
)

# Temporary in-memory storage. A real database replaces this in Level 2.
TASKS: list[dict[str, Any]] = [
    {"id": 1, "title": "Set up TaskFlow", "description": None, "priority": "high", "done": True},
    {"id": 2, "title": "Learn path parameters", "description": None, "priority": "medium", "done": False},
    {"id": 3, "title": "Write the README", "description": "Explain how to run the API", "priority": "low", "done": False},
]

TaskId = Annotated[int, Path(ge=1)]


def get_task_or_404(task_id: int) -> dict[str, Any]:
    for task in TASKS:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Liveness check used by load balancers and monitoring."""
    return {"status": "ok"}


@app.get("/tasks", response_model=list[TaskRead], tags=["tasks"])
def list_tasks(
    done: bool | None = None,
    priority: Priority | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    tasks = TASKS
    if done is not None:
        tasks = [t for t in tasks if t["done"] == done]
    if priority is not None:
        tasks = [t for t in tasks if t["priority"] == priority.value]
    return tasks[:limit]


@app.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate):
    next_id = max((t["id"] for t in TASKS), default=0) + 1
    task = {"id": next_id, **payload.model_dump(mode="json"), "done": False}
    TASKS.append(task)
    return task


@app.get("/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
def get_task(task_id: TaskId):
    return get_task_or_404(task_id)


@app.patch("/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
def update_task(task_id: TaskId, payload: TaskUpdate):
    task = get_task_or_404(task_id)
    task.update(payload.model_dump(mode="json", exclude_unset=True))
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: TaskId) -> None:
    TASKS.remove(get_task_or_404(task_id))
