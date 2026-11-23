import threading

import pytest

from solution import OnceCache


def test_basic():
    cache = OnceCache()
    assert cache.get_or_compute("a", lambda k: k.upper()) == "A"
    assert cache.get_or_compute("a", lambda k: "other") == "A"
    assert len(cache) == 1


def test_different_keys():
    cache = OnceCache()
    cache.get_or_compute(1, lambda k: k * 2)
    cache.get_or_compute(2, lambda k: k * 2)
    assert len(cache) == 2


def test_value_none_is_stored_too():
    cache = OnceCache()
    calls = []

    def compute(k):
        calls.append(k)
        return None

    assert cache.get_or_compute("x", compute) is None
    assert cache.get_or_compute("x", compute) is None
    assert calls == ["x"], "a stored None must not be computed again"


def test_error_stores_nothing_and_retries():
    cache = OnceCache()

    def boom(k):
        raise RuntimeError("no")

    with pytest.raises(RuntimeError):
        cache.get_or_compute("a", boom)
    assert len(cache) == 0
    assert cache.get_or_compute("a", lambda k: "fine") == "fine"


def test_compute_runs_once_with_many_threads():
    cache = OnceCache()
    calls = []
    start = threading.Barrier(8, timeout=5)
    results = []

    def compute(key):
        calls.append(key)
        threading.Event().wait(0.01)      # makes a race very likely if there is no lock
        return key * 2

    def worker():
        start.wait()
        results.append(cache.get_or_compute(21, compute))

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(calls) == 1, f"compute ran {len(calls)} times, it must run once"
    assert results == [42] * 8
