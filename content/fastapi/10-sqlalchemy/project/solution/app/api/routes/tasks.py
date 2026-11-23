from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status

from app.api.deps import TaskServiceDep
from app.schemas.task import Priority, TaskCreate, TaskRead, TaskUpdate
from app.services.task_service import TaskNotFoundError

router = APIRouter(prefix="/tasks", tags=["tasks"])

TaskId = Annotated[int, Path(ge=1)]


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.get("", response_model=list[TaskRead])
def list_tasks(
    service: TaskServiceDep,
    done: bool | None = None,
    priority: Priority | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return service.list(done=done, priority=priority, limit=limit)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, service: TaskServiceDep):
    return service.create(payload)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: TaskId, service: TaskServiceDep):
    try:
        return service.get(task_id)
    except TaskNotFoundError:
        raise _not_found() from None


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: TaskId, payload: TaskUpdate, service: TaskServiceDep):
    try:
        return service.update(task_id, payload)
    except TaskNotFoundError:
        raise _not_found() from None


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: TaskId, service: TaskServiceDep) -> None:
    try:
        service.delete(task_id)
    except TaskNotFoundError:
        raise _not_found() from None
