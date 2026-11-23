from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Task


class SqlAlchemyTaskRepository:
    """Task storage using the SQLAlchemy ORM. The session is provided per request."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self, done: bool | None = None, priority: str | None = None, limit: int = 20) -> list[Task]:
        stmt = select(Task)
        if done is not None:
            stmt = stmt.where(Task.done.is_(done))
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        return list(self.session.scalars(stmt.order_by(Task.id).limit(limit)))

    def get(self, task_id: int) -> Task | None:
        return self.session.get(Task, task_id)

    def add(self, data: dict[str, Any]) -> Task:
        task = Task(**data)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def update(self, task_id: int, changes: dict[str, Any]) -> Task | None:
        task = self.get(task_id)
        if task is None:
            return None
        for field, value in changes.items():
            setattr(task, field, value)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete(self, task_id: int) -> bool:
        task = self.get(task_id)
        if task is None:
            return False
        self.session.delete(task)
        self.session.commit()
        return True
