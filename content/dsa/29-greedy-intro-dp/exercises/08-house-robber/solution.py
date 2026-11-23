def rob(nums):
    skip, take = 0, 0
    for money in nums:
        skip, take = max(skip, take), skip + money
    return max(skip, take)
