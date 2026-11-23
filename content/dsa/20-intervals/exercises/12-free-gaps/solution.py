def free_gaps(meetings, lo, hi):
    gaps = []
    cursor = lo
    for start, end in sorted(meetings):
        if start >= hi:
            break
        if start > cursor:
            gaps.append([cursor, start])
        cursor = max(cursor, end)
    if cursor < hi:
        gaps.append([cursor, hi])
    return gaps
