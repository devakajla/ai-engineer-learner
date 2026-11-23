import time


def retry(fn, attempts=3, base_delay=0.5, retry_on=(ConnectionError, TimeoutError), sleep=time.sleep):
    return fn()
