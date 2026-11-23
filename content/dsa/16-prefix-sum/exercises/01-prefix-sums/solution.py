def prefix_sums(nums):
    result = []
    total = 0
    for x in nums:
        total += x
        result.append(total)
    return result
