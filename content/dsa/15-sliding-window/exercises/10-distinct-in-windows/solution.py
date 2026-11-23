def distinct_in_windows(nums, k):
    counts = {}
    result = []
    for i, x in enumerate(nums):
        counts[x] = counts.get(x, 0) + 1
        if i >= k:
            old = nums[i - k]
            counts[old] -= 1
            if counts[old] == 0:
                del counts[old]
        if i >= k - 1:
            result.append(len(counts))
    return result
