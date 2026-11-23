from typing import Literal, TypedDict, get_args

Status = Literal["todo", "doing", "done"]


class TaskDict(TypedDict):
    id: int
    title: str
    status: Status


_ORDER: tuple[Status, ...] = get_args(Status)


def next_status(status: Status) -> Status:
    i = _ORDER.index(status)
    return _ORDER[min(i + 1, len(_ORDER) - 1)]


def parse_task(data: dict[str, object]) -> TaskDict:
    task_id, title, status = data.get("id"), data.get("title"), data.get("status")
    if not isinstance(task_id, int) or isinstance(task_id, bool):
        raise ValueError("id must be an int")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title must be a non-empty string")
    if status not in _ORDER:
        raise ValueError(f"status must be one of {_ORDER}")
    return {"id": task_id, "title": title, "status": status}
