from collections.abc import Callable, Iterable


def average(nums):
    return sum(nums) / len(nums)


def find_user(users, user_id):
    return users.get(user_id)


def apply_all(fn, items):
    return [fn(i) for i in items]


def pair(a, b):
    return (a, b)


def counts(words):
    result = {}
    for w in words:
        result[w] = result.get(w, 0) + 1
    return result
