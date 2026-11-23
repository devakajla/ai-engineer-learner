def max_meetings(meetings):
    count = 0
    last_end = float("-inf")
    for end, start in sorted((end, start) for start, end in meetings):
        if start >= last_end:
            count += 1
            last_end = end
    return count
