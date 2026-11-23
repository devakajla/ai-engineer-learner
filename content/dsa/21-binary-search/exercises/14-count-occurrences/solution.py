def count_occurrences(nums, target):
    def first_ge(x):
        lo, hi = 0, len(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if nums[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        return lo

    return first_ge(target + 1) - first_ge(target)
