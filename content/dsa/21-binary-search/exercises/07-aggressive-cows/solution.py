def max_min_distance(stalls, cows):
    stalls = sorted(stalls)

    def can_place(d):
        placed = 1
        last = stalls[0]
        for s in stalls[1:]:
            if s - last >= d:
                placed += 1
                last = s
        return placed >= cows

    lo, hi = 1, stalls[-1] - stalls[0]
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        if can_place(mid):
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best
