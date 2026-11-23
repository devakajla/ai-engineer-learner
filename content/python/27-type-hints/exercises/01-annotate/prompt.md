# Annotate the functions

The functions in the starter work, but have no type hints. Add **exact** annotations (the tests read them with `typing.get_type_hints`):

| Function | Parameters | Returns |
|---|---|---|
| `average(nums)` | `nums: list[float]` | `float` |
| `find_user(users, user_id)` | `users: dict[int, str]`, `user_id: int` | `str \| None` |
| `apply_all(fn, items)` | `fn: Callable[[int], int]`, `items: Iterable[int]` | `list[int]` |
| `pair(a, b)` | `a: str`, `b: int` | `tuple[str, int]` |
| `counts(words)` | `words: Iterable[str]` | `dict[str, int]` |

Import `Callable` and `Iterable` from `collections.abc`. Don't change the function bodies.
