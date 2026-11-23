def length_of_lis(nums):
    best = []
    for i, x in enumerate(nums):
        longest = 0
        for j in range(i):
            if nums[j] < x and best[j] > longest:
                longest = best[j]
        best.append(longest + 1)
    return max(best, default=0)
