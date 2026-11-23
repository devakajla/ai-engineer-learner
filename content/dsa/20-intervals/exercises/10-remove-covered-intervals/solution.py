def remove_covered(intervals):
    remaining = 0
    max_end = None
    for start, neg_end in sorted((s, -e) for s, e in intervals):
        end = -neg_end
        if max_end is None or end > max_end:
            remaining += 1
            max_end = end
    return remaining
