def min_removals(intervals):
    removed = 0
    last_end = None
    for end, start in sorted((e, s) for s, e in intervals):
        if last_end is None or start >= last_end:
            last_end = end
        else:
            removed += 1
    return removed
