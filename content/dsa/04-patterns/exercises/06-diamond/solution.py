def diamond(n):
    rows = []
    for i in range(1, n + 1):
        rows.append(" " * (n - i) + "*" * (2 * i - 1))
    for i in range(n - 1, 0, -1):
        rows.append(" " * (n - i) + "*" * (2 * i - 1))
    return rows
