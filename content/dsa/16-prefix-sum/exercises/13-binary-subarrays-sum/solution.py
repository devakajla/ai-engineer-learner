def binary_subarrays_sum(nums, goal):
    seen = {0: 1}
    total = 0
    count = 0
    for x in nums:
        total += x
        count += seen.get(total - goal, 0)
        seen[total] = seen.get(total, 0) + 1
    return count
