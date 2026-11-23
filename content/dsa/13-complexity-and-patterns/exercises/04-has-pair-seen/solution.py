def has_pair(nums, target):
    seen = set()
    for x in nums:
        if target - x in seen:
            return True
        seen.add(x)
    return False
