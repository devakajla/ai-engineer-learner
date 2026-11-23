import functools
import time

TIMINGS: list[tuple[str, float]] = []


def timed(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
    return wrapper
