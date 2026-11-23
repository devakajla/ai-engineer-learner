import time


def best_time(func, rounds=3, timer=time.perf_counter):
    if rounds < 1:
        raise ValueError("rounds must be at least 1")
    times = []
    for _ in range(rounds):
        start = timer()
        func()
        times.append(timer() - start)
    return min(times)


def first_duplicate(iterable):
    seen = set()
    for item in iterable:
        if item in seen:
            return item
        seen.add(item)
    return None
