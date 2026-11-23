def longest_mountain(arr):
    n = len(arr)
    up = [0] * n
    down = [0] * n
    for i in range(1, n):
        if arr[i] > arr[i - 1]:
            up[i] = up[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if arr[i] > arr[i + 1]:
            down[i] = down[i + 1] + 1
    best = 0
    for i in range(n):
        if up[i] > 0 and down[i] > 0:
            best = max(best, up[i] + down[i] + 1)
    return best
