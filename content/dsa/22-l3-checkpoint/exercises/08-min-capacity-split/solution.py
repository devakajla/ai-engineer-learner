def min_largest_sum(nums, m):
    def parts(limit):
        count, cur = 1, 0
        for n in nums:
            if cur + n > limit:
                count += 1
                cur = n
            else:
                cur += n
        return count

    lo, hi = max(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if parts(mid) <= m:
            hi = mid
        else:
            lo = mid + 1
    return lo
