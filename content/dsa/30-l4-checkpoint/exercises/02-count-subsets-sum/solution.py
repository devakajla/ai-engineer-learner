def count_subsets(nums, target):
    ways = [1] + [0] * target
    for num in nums:
        for s in range(target, num - 1, -1):
            ways[s] += ways[s - num]
    return ways[target]
