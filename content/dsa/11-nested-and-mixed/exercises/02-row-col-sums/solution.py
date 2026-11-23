def row_col_sums(matrix):
    row_sums = []
    col_sums = [0] * len(matrix[0])
    for row in matrix:
        row_sums.append(sum(row))
        for c in range(len(row)):
            col_sums[c] += row[c]
    return row_sums, col_sums
