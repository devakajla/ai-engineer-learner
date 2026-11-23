from collections.abc import Callable, Iterable


def average(nums: list[float]) -> float:
    return sum(nums) / len(nums)


def find_user(users: dict[int, str], user_id: int) -> str | None:
    return users.get(user_id)


def apply_all(fn: Callable[[int], int], items: Iterable[int]) -> list[int]:
    return [fn(i) for i in items]


def pair(a: str, b: int) -> tuple[str, int]:
    return (a, b)


def counts(words: Iterable[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for w in words:
        result[w] = result.get(w, 0) + 1
    return result
