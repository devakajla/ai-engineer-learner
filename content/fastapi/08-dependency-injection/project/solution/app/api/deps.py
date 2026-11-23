"""Shared FastAPI dependencies: how routes get settings, repositories and services."""

from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.repositories.task_repository import SEED, InMemoryTaskRepository
from app.services.task_service import TaskService

SettingsDep = Annotated[Settings, Depends(get_settings)]

# One in-memory store for the whole process (replaced by a database in the next steps).
_task_repository = InMemoryTaskRepository(seed=SEED)


def get_task_repository() -> InMemoryTaskRepository:
    return _task_repository


def get_task_service(
    repo: Annotated[InMemoryTaskRepository, Depends(get_task_repository)],
) -> TaskService:
    return TaskService(repo)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
