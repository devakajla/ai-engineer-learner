def max_overlap(intervals):
    events = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end + 1, -1))
    events.sort()
    current = best = 0
    for _, change in events:
        current += change
        best = max(best, current)
    return best
