def missing_number(nums):
    full = set(range(len(nums) + 1))
    missing = full - set(nums)
    return missing.pop()
