def min_subarray(nums):
    ending_here = best = nums[0]
    for x in nums[1:]:
        ending_here = min(x, ending_here + x)
        best = min(best, ending_here)
    return best
