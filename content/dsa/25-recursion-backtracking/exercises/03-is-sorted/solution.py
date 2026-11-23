def is_sorted(nums):
    if len(nums) < 2:
        return True
    return nums[0] <= nums[1] and is_sorted(nums[1:])
