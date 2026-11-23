def num_ways_split(nums):
    total = sum(nums)
    left = 0
    count = 0
    for i in range(len(nums) - 1):
        left += nums[i]
        if left >= total - left:
            count += 1
    return count
