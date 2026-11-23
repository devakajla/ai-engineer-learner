import threading

from solution import SafeCounter


def test_basic():
    c = SafeCounter()
    assert c.value == 0
    c.increment()
    c.increment(5)
    assert c.value == 6, "increment() adds 1, increment(5) adds 5"


def test_start_and_reset():
    c = SafeCounter(10)
    assert c.value == 10
    c.increment(2)
    c.reset()
    assert c.value == 0, "reset() must set the value to 0"


def test_many_threads_lose_no_updates():
    c = SafeCounter()

    def work():
        for _ in range(5000):
            c.increment()

    threads = [threading.Thread(target=work) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert c.value == 40000, f"expected 40000, got {c.value} (lost updates -> use a Lock)"


def test_has_a_lock():
    c = SafeCounter()
    lock_type = type(threading.Lock())
    assert any(isinstance(v, lock_type) for v in vars(c).values()), "keep a threading.Lock on the object"
