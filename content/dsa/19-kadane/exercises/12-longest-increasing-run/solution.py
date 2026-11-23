def longest_increasing_run(nums):
    best = run = 0
    for i, x in enumerate(nums):
        if i > 0 and x > nums[i - 1]:
            run += 1
        else:
            run = 1
        best = max(best, run)
    return best
