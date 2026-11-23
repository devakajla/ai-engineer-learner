def longest_sum_at_most(nums, k):
    total = 0
    lo = 0
    best = 0
    for hi, x in enumerate(nums):
        total += x
        while total > k:
            total -= nums[lo]
            lo += 1
        best = max(best, hi - lo + 1)
    return best
