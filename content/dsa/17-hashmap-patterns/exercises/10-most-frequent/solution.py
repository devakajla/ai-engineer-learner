def most_frequent(nums):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    best = None
    for value, n in counts.items():
        if best is None or n > counts[best] or (n == counts[best] and value < best):
            best = value
    return best
