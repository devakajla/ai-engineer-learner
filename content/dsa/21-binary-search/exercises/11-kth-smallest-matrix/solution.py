def kth_smallest(matrix, k):
    n = len(matrix)

    def count_le(x):
        count = 0
        col = n - 1
        for row in range(n):
            while col >= 0 and matrix[row][col] > x:
                col -= 1
            count += col + 1
        return count

    lo, hi = matrix[0][0], matrix[-1][-1]
    while lo < hi:
        mid = (lo + hi) // 2
        if count_le(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
