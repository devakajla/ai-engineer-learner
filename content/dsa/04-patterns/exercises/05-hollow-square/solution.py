def hollow_square(n):
    rows = []
    for i in range(n):
        if i == 0 or i == n - 1:
            rows.append("*" * n)
        else:
            rows.append("*" + " " * (n - 2) + "*")
    return rows
