def can_cover(intervals, lo, hi):
    needed = lo
    for start, end in sorted(intervals):
        if start > needed:
            break
        needed = max(needed, end + 1)
    return needed > hi
