def covered_length(intervals):
    total = 0
    reach = None
    for start, end in sorted(intervals):
        if reach is None or start > reach:
            total += end - start
            reach = end
        elif end > reach:
            total += end - reach
            reach = end
    return total
