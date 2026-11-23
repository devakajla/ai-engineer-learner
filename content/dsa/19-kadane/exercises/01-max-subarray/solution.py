def max_subarray(nums):
    ending_here = best = nums[0]
    for x in nums[1:]:
        ending_here = max(x, ending_here + x)
        best = max(best, ending_here)
    return best
