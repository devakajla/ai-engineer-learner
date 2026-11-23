from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.api.deps import TaskServiceDep
from app.schemas.task import Priority, TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])

TaskId = Annotated[int, Path(ge=1)]

# Domain errors (e.g. TaskNotFoundError) are turned into HTTP responses by app/api/errors.py.


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    service: TaskServiceDep,
    done: bool | None = None,
    priority: Priority | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await service.list(done=done, priority=priority, limit=limit)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, service: TaskServiceDep):
    return await service.create(payload)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: TaskId, service: TaskServiceDep):
    return await service.get(task_id)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(task_id: TaskId, payload: TaskUpdate, service: TaskServiceDep):
    return await service.update(task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: TaskId, service: TaskServiceDep) -> None:
    await service.delete(task_id)
