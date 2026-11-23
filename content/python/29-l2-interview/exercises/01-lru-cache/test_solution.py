import time

from solution import LRUCache


def test_example():
    c = LRUCache(2)
    c.put(1, "a")
    c.put(2, "b")
    assert c.get(1) == "a"
    c.put(3, "c")
    assert c.get(2) == -1
    assert c.get(3) == "c" and c.get(1) == "a"
    assert len(c) == 2


def test_update_refreshes():
    c = LRUCache(2)
    c.put("x", 1)
    c.put("y", 2)
    c.put("x", 10)      # x becomes most recent
    c.put("z", 3)       # evicts y
    assert c.get("y") == -1 and c.get("x") == 10


def test_capacity_one():
    c = LRUCache(1)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == -1 and c.get(2) == 2


def test_o1_performance():
    c = LRUCache(50_000)
    start = time.perf_counter()
    for i in range(200_000):
        c.put(i, i)
        c.get(i - 10)
    assert time.perf_counter() - start < 3, "operations must be O(1)"
