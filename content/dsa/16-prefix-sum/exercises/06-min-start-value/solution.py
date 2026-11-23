def min_start_value(nums):
    total = 0
    low = 0
    for x in nums:
        total += x
        low = min(low, total)
    return 1 - low
