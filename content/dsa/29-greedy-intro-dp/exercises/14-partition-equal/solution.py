def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    ok = [True] + [False] * target
    for num in nums:
        for s in range(target, num - 1, -1):
            if ok[s - num]:
                ok[s] = True
    return ok[target]
