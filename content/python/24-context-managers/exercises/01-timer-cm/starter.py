import time
from contextlib import contextmanager


class Timer:
    pass


@contextmanager
def timer(results, label):
    start = time.perf_counter()
    yield
    results.append((label, time.perf_counter() - start))
