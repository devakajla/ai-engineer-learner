import threading

import pytest

from solution import pipeline


def test_keeps_input_order():
    assert pipeline([1, 2, 3, 4], lambda x: x * 10) == [10, 20, 30, 40]


def test_empty():
    assert pipeline([], str) == []


def test_more_items_than_workers():
    assert pipeline(list(range(50)), lambda x: x + 1, workers=3) == list(range(1, 51))


def test_single_worker():
    assert pipeline(["a", "b"], str.upper, workers=1) == ["A", "B"]


def test_all_threads_finished():
    before = threading.active_count()
    pipeline(list(range(20)), lambda x: x, workers=4)
    assert threading.active_count() == before, "all worker threads must be joined before returning"


def test_uses_several_threads():
    names = set()

    def job(x):
        names.add(threading.current_thread().name)
        return x

    barrier = threading.Barrier(2, timeout=5)

    def waiting(x):
        barrier.wait()
        return job(x)

    assert pipeline([1, 2], waiting, workers=2) == [1, 2], "two workers must run at the same time"
    assert len(names) == 2


def test_bad_workers():
    with pytest.raises(ValueError):
        pipeline([1], str, workers=0)
