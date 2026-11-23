from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task


# Whitelist: API sort names -> columns. Never put user input straight into ORDER BY.
SORTABLE = {"id": Task.id, "created_at": Task.created_at, "due_date": Task.due_date, "title": Task.title}


class SqlAlchemyTaskRepository:
    """Task storage using async SQLAlchemy. The session is provided per request."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        *,
        done: bool | None = None,
        priority: str | None = None,
        q: str | None = None,
        sort: str = "-id",
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        """Return one page of tasks and the total count matching the filters."""
        filters = []
        if done is not None:
            filters.append(Task.done.is_(done))
        if priority is not None:
            filters.append(Task.priority == priority)
        if q:
            filters.append(Task.title.ilike(f"%{q}%"))  # bound parameter, not string SQL

        column = SORTABLE[sort.lstrip("-")]
        order = column.desc() if sort.startswith("-") else column.asc()
        tiebreak = Task.id.desc() if sort.startswith("-") else Task.id.asc()

        stmt = select(Task).where(*filters).order_by(order, tiebreak).limit(limit).offset(offset)
        total = await self.session.scalar(select(func.count()).select_from(Task).where(*filters))
        return list(await self.session.scalars(stmt)), total or 0

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
