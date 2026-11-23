def transpose(matrix):
    result = []
    for c in range(len(matrix[0])):
        new_row = []
        for r in range(len(matrix)):
            new_row.append(matrix[r][c])
        result.append(new_row)
    return result
