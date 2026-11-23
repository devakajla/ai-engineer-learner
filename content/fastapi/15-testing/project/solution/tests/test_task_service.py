"""Unit tests: the service with a fake repository — no HTTP, no database."""

import asyncio

import pytest

from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskNotFoundError, TaskService


class FakeRepo:
    def __init__(self):
        self.items: dict[int, dict] = {}

    async def list(self, **kwargs):
        return list(self.items.values()), len(self.items)

    async def get(self, task_id):
        return self.items.get(task_id)

    async def add(self, data):
        task = {"id": len(self.items) + 1, **data}
        self.items[task["id"]] = task
        return task

    async def update(self, task_id, changes):
        if task_id not in self.items:
            return None
        self.items[task_id].update(changes)
        return self.items[task_id]

    async def delete(self, task_id):
        return self.items.pop(task_id, None) is not None


def test_create_sets_done_false():
    repo = FakeRepo()
    task = asyncio.run(TaskService(repo).create(TaskCreate(title="x", priority="low")))
    assert task["done"] is False and task["priority"] == "low"


def test_missing_raises_domain_error():
    service = TaskService(FakeRepo())
    with pytest.raises(TaskNotFoundError):
        asyncio.run(service.get(1))
    with pytest.raises(TaskNotFoundError):
        asyncio.run(service.update(1, TaskUpdate(done=True)))
    with pytest.raises(TaskNotFoundError):
        asyncio.run(service.delete(1))
