def can_make_sum(nums, target):
    ok = [True] + [False] * target
    for num in nums:
        for s in range(target, num - 1, -1):
            if ok[s - num]:
                ok[s] = True
    return ok[target]
