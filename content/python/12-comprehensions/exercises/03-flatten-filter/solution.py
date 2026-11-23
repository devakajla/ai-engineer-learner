def flatten_positive(matrix):
    return [n for row in matrix for n in row if n > 0]
