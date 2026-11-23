def k_diff_pairs(nums, k):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    pairs = 0
    for x, n in counts.items():
        if k == 0:
            if n >= 2:
                pairs += 1
        elif x + k in counts:
            pairs += 1
    return pairs
