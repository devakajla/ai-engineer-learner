from app.core.errors import NotFoundError
from app.db.models import Task
from app.repositories.base import TaskRepository
from app.schemas.task import Priority, TaskCreate, TaskSort, TaskUpdate


class TaskNotFoundError(NotFoundError):
    """Raised when a task id does not exist."""

    def __init__(self, task_id: int) -> None:
        super().__init__("Task not found")
        self.task_id = task_id


class TaskService:
    """Business rules for tasks. Knows nothing about HTTP or which database is used."""

    def __init__(self, repo: TaskRepository) -> None:
        self.repo = repo

    async def list(
        self,
        *,
        done: bool | None = None,
        priority: Priority | None = None,
        q: str | None = None,
        sort: TaskSort = "-id",
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        return await self.repo.list(
            done=done,
            priority=priority.value if priority else None,
            q=q,
            sort=sort,
            limit=limit,
            offset=offset,
        )

    async def get(self, task_id: int) -> Task:
        task = await self.repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    async def create(self, data: TaskCreate) -> Task:
        return await self.repo.add({**data.model_dump(), "done": False})

    async def update(self, task_id: int, data: TaskUpdate) -> Task:
        task = await self.repo.update(task_id, data.model_dump(exclude_unset=True))
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    async def delete(self, task_id: int) -> None:
        if not await self.repo.delete(task_id):
            raise TaskNotFoundError(task_id)
