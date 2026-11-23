import functools
import time


def ttl_cache(seconds, clock=time.monotonic):
    def decorator(func):
        cache: dict = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = clock()
            hit = cache.get(key)
            if hit is not None and now - hit[0] < seconds:
                return hit[1]
            value = func(*args, **kwargs)
            cache[key] = (now, value)
            return value

        wrapper.cache_clear = cache.clear
        return wrapper

    return decorator
