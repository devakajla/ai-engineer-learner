# A generic Stack[T]

Write a generic class `Stack[T]` (use the 3.12 syntax `class Stack[T]:` or `Generic[T]`):

- `push(item: T) -> None`
- `pop() -> T` — raises `IndexError("pop from empty stack")` when empty
- `peek() -> T | None` — top item or `None`
- `__len__` and `__bool__` (empty stack is falsy)
- `Stack.from_items(items: Iterable[T]) -> Stack[T]` — a classmethod that pushes items in order

And a generic function `last_or_default[T](items: Sequence[T], default: T) -> T`.

```python
s: Stack[int] = Stack.from_items([1, 2, 3])
s.pop(), s.peek(), len(s)       # -> (3, 2, 2)
last_or_default([], "none")     # -> "none"
```
