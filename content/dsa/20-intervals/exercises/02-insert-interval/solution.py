def insert_interval(intervals, new):
    result = []
    i = 0
    n = len(intervals)
    while i < n and intervals[i][1] < new[0]:
        result.append(list(intervals[i]))
        i += 1
    start, end = new
    while i < n and intervals[i][0] <= end:
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        i += 1
    result.append([start, end])
    while i < n:
        result.append(list(intervals[i]))
        i += 1
    return result
