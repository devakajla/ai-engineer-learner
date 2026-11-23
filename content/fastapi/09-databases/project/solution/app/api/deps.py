"""Shared FastAPI dependencies: how routes get settings, repositories and services."""

from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.repositories.base import TaskRepository
from app.repositories.sqlite_task_repository import SqliteTaskRepository
from app.services.task_service import TaskService

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_task_repository(settings: SettingsDep) -> TaskRepository:
    return SqliteTaskRepository(settings.database_path)


def get_task_service(repo: Annotated[TaskRepository, Depends(get_task_repository)]) -> TaskService:
    return TaskService(repo)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
