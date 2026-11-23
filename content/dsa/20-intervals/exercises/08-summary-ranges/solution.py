def summary_ranges(nums):
    result = []
    i = 0
    while i < len(nums):
        start = nums[i]
        while i + 1 < len(nums) and nums[i + 1] == nums[i] + 1:
            i += 1
        result.append(str(start) if nums[i] == start else f"{start}->{nums[i]}")
        i += 1
    return result
