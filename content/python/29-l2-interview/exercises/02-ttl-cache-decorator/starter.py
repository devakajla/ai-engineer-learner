import functools
import time


def ttl_cache(seconds, clock=time.monotonic):
    def decorator(func):
        return func
    return decorator
