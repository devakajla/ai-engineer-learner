import functools
import time


def retry(attempts=3, exceptions=(Exception,), base_delay=0.5, sleep=time.sleep):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                wrapper.attempts_made = attempt
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == attempts:
                        raise
                    sleep(base_delay * 2 ** (attempt - 1))

        wrapper.attempts_made = 0
        return wrapper

    return decorator
