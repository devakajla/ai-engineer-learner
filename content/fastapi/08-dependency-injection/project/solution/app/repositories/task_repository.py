from typing import Any

Task = dict[str, Any]

SEED: list[Task] = [
    {"id": 1, "title": "Set up TaskFlow", "description": None, "priority": "high", "done": True},
    {"id": 2, "title": "Learn path parameters", "description": None, "priority": "medium", "done": False},
    {"id": 3, "title": "Write the README", "description": "Explain how to run the API", "priority": "low", "done": False},
]


class InMemoryTaskRepository:
    """Storage only. Replaced by a database repository in Level 2."""

    def __init__(self, seed: list[Task] | None = None) -> None:
        self._tasks: dict[int, Task] = {t["id"]: dict(t) for t in (seed or [])}
        self._next_id = max(self._tasks, default=0) + 1

    def list(self) -> list[Task]:
        return list(self._tasks.values())

    def get(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def add(self, data: Task) -> Task:
        task = {"id": self._next_id, **data}
        self._tasks[task["id"]] = task
        self._next_id += 1
        return task

    def update(self, task_id: int, changes: Task) -> Task | None:
        task = self._tasks.get(task_id)
        if task is not None:
            task.update(changes)
        return task

    def delete(self, task_id: int) -> bool:
        return self._tasks.pop(task_id, None) is not None
