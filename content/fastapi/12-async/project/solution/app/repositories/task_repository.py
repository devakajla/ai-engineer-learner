from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task


class SqlAlchemyTaskRepository:
    """Task storage using async SQLAlchemy. The session is provided per request."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, done: bool | None = None, priority: str | None = None, limit: int = 20) -> list[Task]:
        stmt = select(Task)
        if done is not None:
            stmt = stmt.where(Task.done.is_(done))
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        return list(await self.session.scalars(stmt.order_by(Task.id).limit(limit)))

    async def get(self, task_id: int) -> Task | None:
        return await self.session.get(Task, task_id)

    async def add(self, data: dict[str, Any]) -> Task:
        task = Task(**data)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update(self, task_id: int, changes: dict[str, Any]) -> Task | None:
        task = await self.get(task_id)
        if task is None:
            return None
        for field, value in changes.items():
            setattr(task, field, value)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task_id: int) -> bool:
        task = await self.get(task_id)
        if task is None:
            return False
        await self.session.delete(task)
        await self.session.commit()
        return True
