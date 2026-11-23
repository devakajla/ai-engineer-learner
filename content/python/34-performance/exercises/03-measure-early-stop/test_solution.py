import itertools

import pytest

from solution import best_time, first_duplicate


def test_best_time_returns_smallest():
    ticks = iter([0, 2, 10, 13, 20, 21])
    assert best_time(lambda: None, rounds=3, timer=lambda: next(ticks)) == 1


def test_best_time_calls_func_each_round():
    calls = []
    ticks = itertools.count()
    best_time(lambda: calls.append(1), rounds=4, timer=lambda: next(ticks))
    assert len(calls) == 4


def test_best_time_reads_timer_before_and_after_each_call():
    events = []
    ticks = itertools.count()

    def timer():
        events.append("timer")
        return next(ticks)

    def func():
        events.append("func")

    best_time(func, rounds=2, timer=timer)
    assert events == ["timer", "func", "timer", "timer", "func", "timer"]


def test_best_time_single_round():
    ticks = iter([5, 9])
    assert best_time(lambda: None, rounds=1, timer=lambda: next(ticks)) == 4


def test_best_time_default_timer_works():
    assert best_time(lambda: sum(range(100))) >= 0


def test_best_time_bad_rounds():
    with pytest.raises(ValueError):
        best_time(lambda: None, rounds=0)


def test_first_duplicate_basic():
    assert first_duplicate([4, 7, 2, 7, 4]) == 7
    assert first_duplicate([1, 2, 3]) is None
    assert first_duplicate([]) is None


def test_first_duplicate_strings():
    assert first_duplicate("abcdbe") == "b"


def test_first_duplicate_stops_early():
    read = []

    def numbers():
        for n in itertools.count():
            read.append(n)
            yield n % 100          # the first repeat is the 101st item

    assert first_duplicate(numbers()) == 0
    assert len(read) == 101, f"read {len(read)} items, it should stop at the first duplicate (101)"


def test_first_duplicate_works_on_endless_iterable():
    assert first_duplicate(itertools.cycle([1, 2, 3])) == 1
