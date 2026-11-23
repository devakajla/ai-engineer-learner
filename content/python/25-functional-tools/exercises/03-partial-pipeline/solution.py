import re
from functools import partial, reduce
from itertools import accumulate


def compose(*funcs):
    return lambda x: reduce(lambda acc, f: f(acc), funcs, x)


def make_cleaner():
    return compose(str.strip, str.lower, partial(re.sub, r"\s+", "-"), lambda s: s[:20])


def running_max(nums):
    return list(accumulate(nums, max))
