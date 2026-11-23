def pyramid(n):
    rows = []
    for i in range(1, n + 1):
        rows.append(" " * (n - i) + "*" * (2 * i - 1))
    return rows
