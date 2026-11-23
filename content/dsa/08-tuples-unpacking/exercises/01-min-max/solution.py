def min_max(nums):
    low = high = nums[0]
    for n in nums:
        if n < low:
            low = n
        if n > high:
            high = n
    return low, high
