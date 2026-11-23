def triplets_smaller(nums, target):
    nums = sorted(nums)
    n = len(nums)
    count = 0
    for i in range(n - 2):
        left, right = i + 1, n - 1
        while left < right:
            if nums[i] + nums[left] + nums[right] < target:
                count += right - left
                left += 1
            else:
                right -= 1
    return count
