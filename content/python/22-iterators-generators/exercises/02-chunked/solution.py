from itertools import islice


def chunked(iterable, size):
    if size < 1:
        raise ValueError("size must be >= 1")
    return _chunks(iter(iterable), size)


def _chunks(it, size):
    while batch := list(islice(it, size)):
        yield batch
