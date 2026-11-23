def first_duplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return x
        seen.add(x)
    return None
