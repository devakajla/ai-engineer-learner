from collections.abc import Iterable, Sequence


class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T | None:
        return self._items[-1] if self._items else None

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    @classmethod
    def from_items(cls, items: Iterable[T]) -> "Stack[T]":
        stack = cls()
        for item in items:
            stack.push(item)
        return stack


def last_or_default[T](items: Sequence[T], default: T) -> T:
    return items[-1] if items else default
