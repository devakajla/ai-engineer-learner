def remove_interval(intervals, remove):
    x, y = remove
    result = []
    for a, b in intervals:
        left_end = min(b, x)
        if a < left_end:
            result.append([a, left_end])
        right_start = max(a, y)
        if right_start < b:
            result.append([right_start, b])
    return result
