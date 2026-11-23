def region_sums(matrix, queries):
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    p = [[0] * (cols + 1) for _ in range(rows + 1)]
    for i in range(rows):
        for j in range(cols):
            p[i + 1][j + 1] = matrix[i][j] + p[i][j + 1] + p[i + 1][j] - p[i][j]
    return [p[r2 + 1][c2 + 1] - p[r1][c2 + 1] - p[r2 + 1][c1] + p[r1][c1] for r1, c1, r2, c2 in queries]
