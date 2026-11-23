def closest_to_zero(nums):
    best = nums[0]
    for n in nums:
        if abs(n) < abs(best) or (abs(n) == abs(best) and n > best):
            best = n
    return best, abs(best)
