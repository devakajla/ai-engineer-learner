def longest_sum_k(nums, k):
    first = {0: -1}
    total = 0
    best = 0
    for i, x in enumerate(nums):
        total += x
        if total - k in first:
            best = max(best, i - first[total - k])
        if total not in first:
            first[total] = i
    return best
