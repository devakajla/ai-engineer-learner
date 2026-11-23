def max_sum_one_deletion(nums):
    keep = nums[0]          # best sum ending here, nothing deleted
    deleted = float("-inf")  # best sum ending here, one element deleted
    best = nums[0]
    for x in nums[1:]:
        deleted = max(keep, deleted + x)
        keep = max(x, keep + x)
        best = max(best, keep, deleted)
    return best
