def count_divisible(nums, k):
    seen = {0: 1}
    prefix = 0
    total = 0
    for n in nums:
        prefix = (prefix + n) % k
        total += seen.get(prefix, 0)
        seen[prefix] = seen.get(prefix, 0) + 1
    return total
