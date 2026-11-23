"""Shared FastAPI dependencies: how routes get settings, DB sessions, repositories and services."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.repositories.base import TaskRepository
from app.repositories.task_repository import SqlAlchemyTaskRepository
from app.services.task_service import TaskService

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSession = Annotated[Session, Depends(get_db)]


def get_task_repository(db: DbSession) -> TaskRepository:
    return SqlAlchemyTaskRepository(db)


def get_task_service(repo: Annotated[TaskRepository, Depends(get_task_repository)]) -> TaskService:
    return TaskService(repo)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
