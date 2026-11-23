def two_sum_less_than_k(nums, k):
    nums = sorted(nums)
    left, right = 0, len(nums) - 1
    best = -1
    while left < right:
        s = nums[left] + nums[right]
        if s < k:
            best = max(best, s)
            left += 1
        else:
            right -= 1
    return best
