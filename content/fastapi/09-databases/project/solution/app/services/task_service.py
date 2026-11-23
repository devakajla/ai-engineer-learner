from app.repositories.base import Task, TaskRepository
from app.schemas.task import Priority, TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    """Raised when a task id does not exist."""


class TaskService:
    """Business rules for tasks. Knows nothing about HTTP or which database is used."""

    def __init__(self, repo: TaskRepository) -> None:
        self.repo = repo

    def list(self, done: bool | None = None, priority: Priority | None = None, limit: int = 20) -> list[Task]:
        return self.repo.list(done=done, priority=priority.value if priority else None, limit=limit)

    def get(self, task_id: int) -> Task:
        task = self.repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def create(self, data: TaskCreate) -> Task:
        return self.repo.add({**data.model_dump(mode="json"), "done": False})

    def update(self, task_id: int, data: TaskUpdate) -> Task:
        task = self.repo.update(task_id, data.model_dump(mode="json", exclude_unset=True))
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def delete(self, task_id: int) -> None:
        if not self.repo.delete(task_id):
            raise TaskNotFoundError(task_id)
