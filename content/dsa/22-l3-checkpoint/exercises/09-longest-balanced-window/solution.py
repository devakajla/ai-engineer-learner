def longest_sum_at_most(nums, k):
    left = 0
    total = 0
    best = 0
    for right, n in enumerate(nums):
        total += n
        while total > k:
            total -= nums[left]
            left += 1
        best = max(best, right - left + 1)
    return best
