def max_increasing_sum(nums):
    best = cur = 0
    for i, x in enumerate(nums):
        if i > 0 and x > nums[i - 1]:
            cur += x
        else:
            cur = x
        best = max(best, cur)
    return best
