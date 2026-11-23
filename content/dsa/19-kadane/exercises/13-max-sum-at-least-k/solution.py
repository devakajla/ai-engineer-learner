def max_sum_at_least_k(nums, k):
    prefix = [0]
    for x in nums:
        prefix.append(prefix[-1] + x)
    best = float("-inf")
    low = float("inf")
    for end in range(k, len(prefix)):
        low = min(low, prefix[end - k])
        best = max(best, prefix[end] - low)
    return best
