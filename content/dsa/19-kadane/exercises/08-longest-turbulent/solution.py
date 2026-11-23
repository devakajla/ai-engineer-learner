def longest_turbulent(arr):
    if not arr:
        return 0
    best = cur = 1
    prev_sign = 0
    for i in range(1, len(arr)):
        if arr[i] > arr[i - 1]:
            sign = 1
        elif arr[i] < arr[i - 1]:
            sign = -1
        else:
            sign = 0
        if sign == 0:
            cur = 1
        elif sign == -prev_sign:
            cur += 1
        else:
            cur = 2
        prev_sign = sign
        best = max(best, cur)
    return best
