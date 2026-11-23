def two_sum_values(nums, target):
    nums = sorted(nums)
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return [nums[left], nums[right]]
        if s < target:
            left += 1
        else:
            right -= 1
    return []
