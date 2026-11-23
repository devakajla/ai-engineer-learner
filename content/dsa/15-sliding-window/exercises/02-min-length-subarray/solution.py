def min_len_subarray(nums, target):
    best = 0
    lo = 0
    total = 0
    for hi in range(len(nums)):
        total += nums[hi]
        while total >= target:
            length = hi - lo + 1
            if best == 0 or length < best:
                best = length
            total -= nums[lo]
            lo += 1
    return best
