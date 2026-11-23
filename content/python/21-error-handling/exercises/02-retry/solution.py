import time


def retry(fn, attempts=3, base_delay=0.5, retry_on=(ConnectionError, TimeoutError), sleep=time.sleep):
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except retry_on:
            if attempt == attempts:
                raise
            sleep(base_delay * 2 ** (attempt - 1))
