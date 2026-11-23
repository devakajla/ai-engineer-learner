def sum_list(nums):
    if not nums:
        return 0
    return nums[0] + sum_list(nums[1:])
