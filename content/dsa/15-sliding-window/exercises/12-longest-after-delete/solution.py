def longest_after_delete(nums):
    zeros = 0
    lo = 0
    best = 0
    for hi, x in enumerate(nums):
        if x == 0:
            zeros += 1
        while zeros > 1:
            if nums[lo] == 0:
                zeros -= 1
            lo += 1
        best = max(best, hi - lo)
    return best
