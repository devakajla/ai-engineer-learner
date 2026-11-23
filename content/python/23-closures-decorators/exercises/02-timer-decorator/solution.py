import functools
import time

TIMINGS: list[tuple[str, float]] = []


def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            TIMINGS.append((func.__name__, time.perf_counter() - start))

    return wrapper
