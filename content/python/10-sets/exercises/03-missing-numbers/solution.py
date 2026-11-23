def missing(nums, n):
    return sorted(set(range(1, n + 1)) - set(nums))
