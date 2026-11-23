def count_product_less(nums, k):
    if k <= 1:
        return 0
    product = 1
    lo = 0
    count = 0
    for hi, x in enumerate(nums):
        product *= x
        while product >= k:
            product //= nums[lo]
            lo += 1
        count += hi - lo + 1
    return count
