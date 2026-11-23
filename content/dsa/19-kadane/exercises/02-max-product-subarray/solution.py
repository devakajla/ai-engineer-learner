def max_product(nums):
    hi = lo = best = nums[0]
    for x in nums[1:]:
        candidates = (x, hi * x, lo * x)
        hi = max(candidates)
        lo = min(candidates)
        best = max(best, hi)
    return best
