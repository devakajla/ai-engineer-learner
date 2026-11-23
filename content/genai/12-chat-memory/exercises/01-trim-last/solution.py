def trim_last(history, n):
    if n <= 0:
        return []
    return history[-n:]
