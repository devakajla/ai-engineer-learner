from dataclasses import dataclass, field


@dataclass(order=True)
class Task:
    sort_index: tuple = field(init=False, repr=False)
    title: str
    priority: int = 2
    tags: list[str] = field(default_factory=list)
    done: bool = False

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("title is required")
        if self.priority not in (1, 2, 3):
            raise ValueError("priority must be 1, 2 or 3")
        self.sort_index = (self.priority, self.title)


@dataclass(frozen=True)
class TaskId:
    value: int
