def int_sqrt(x):
    lo, hi = 0, x
    best = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if mid * mid <= x:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best
