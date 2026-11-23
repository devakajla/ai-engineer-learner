def chunked(iterable, size):
    return [iterable[i:i + size] for i in range(0, len(iterable), size)]
