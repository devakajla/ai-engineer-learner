def make_counter(start=0, step=1):
    value = start

    def counter():
        nonlocal value
        value += step
        return value

    return counter


def make_rate_checker(limit):
    used = 0

    def allow():
        nonlocal used
        if used >= limit:
            return False
        used += 1
        return True

    def reset():
        nonlocal used
        used = 0

    return allow, reset
