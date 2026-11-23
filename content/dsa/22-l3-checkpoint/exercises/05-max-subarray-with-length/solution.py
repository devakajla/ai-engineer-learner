def best_sums(nums, k):
    window = sum(nums[:k])
    best_window = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best_window = max(best_window, window)
    cur = best_any = nums[0]
    for n in nums[1:]:
        cur = max(n, cur + n)
        best_any = max(best_any, cur)
    return (best_window, best_any)
