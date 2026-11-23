def combine(n, k):
    result = []
    current = []

    def go(start):
        if len(current) == k:
            result.append(list(current))
            return
        for i in range(start, n + 1):
            current.append(i)
            go(i + 1)
            current.pop()

    go(1)
    return result
