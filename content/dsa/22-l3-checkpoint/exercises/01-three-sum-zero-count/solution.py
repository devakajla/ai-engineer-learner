def count_zero_triplets(nums):
    nums = sorted(nums)
    count = 0
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            total = nums[i] + nums[lo] + nums[hi]
            if total < 0:
                lo += 1
            elif total > 0:
                hi -= 1
            else:
                count += 1
                lo += 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
                hi -= 1
    return count
