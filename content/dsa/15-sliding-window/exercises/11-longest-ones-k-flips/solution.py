def longest_ones(nums, k):
    zeros = 0
    lo = 0
    best = 0
    for hi, x in enumerate(nums):
        if x == 0:
            zeros += 1
        while zeros > k:
            if nums[lo] == 0:
                zeros -= 1
            lo += 1
        best = max(best, hi - lo + 1)
    return best
