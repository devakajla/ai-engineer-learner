def number_triangle(n):
    rows = []
    for i in range(1, n + 1):
        row = ""
        for j in range(1, i + 1):
            row += str(j)
        rows.append(row)
    return rows
