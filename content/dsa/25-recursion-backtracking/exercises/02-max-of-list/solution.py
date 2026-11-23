def max_of_list(nums):
    if len(nums) == 1:
        return nums[0]
    rest = max_of_list(nums[1:])
    return nums[0] if nums[0] > rest else rest
