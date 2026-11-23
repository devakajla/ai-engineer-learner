import functools
import time


def retry(attempts=3, exceptions=(Exception,), base_delay=0.5, sleep=time.sleep):
    pass
