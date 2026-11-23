def divisible_by_k(nums, k):
    seen = {0: 1}
    total = 0
    count = 0
    for x in nums:
        total = (total + x) % k
        count += seen.get(total, 0)
        seen[total] = seen.get(total, 0) + 1
    return count
