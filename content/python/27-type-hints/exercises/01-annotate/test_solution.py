from collections.abc import Callable, Iterable
from typing import get_type_hints

import solution


def hints(fn):
    return get_type_hints(fn)


def test_average():
    assert hints(solution.average) == {"nums": list[float], "return": float}


def test_find_user():
    assert hints(solution.find_user) == {"users": dict[int, str], "user_id": int, "return": str | None}


def test_apply_all():
    assert hints(solution.apply_all) == {"fn": Callable[[int], int], "items": Iterable[int], "return": list[int]}


def test_pair_and_counts():
    assert hints(solution.pair) == {"a": str, "b": int, "return": tuple[str, int]}
    assert hints(solution.counts) == {"words": Iterable[str], "return": dict[str, int]}


def test_behaviour_unchanged():
    assert solution.average([1.0, 2.0]) == 1.5
    assert solution.counts(["a", "a"]) == {"a": 2}
