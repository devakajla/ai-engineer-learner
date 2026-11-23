def three_sum_closest(nums, target):
    nums = sorted(nums)
    n = len(nums)
    best = nums[0] + nums[1] + nums[2]
    for i in range(n - 2):
        left, right = i + 1, n - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if (abs(s - target), s) < (abs(best - target), best):
                best = s
            if s == target:
                return s
            if s < target:
                left += 1
            else:
                right -= 1
    return best
