def rotate_right(nums, k):
    if not nums:
        return []
    k %= len(nums)
    if k == 0:
        return nums[:]
    return nums[-k:] + nums[:-k]
