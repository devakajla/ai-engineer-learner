def subsets_with_sum(nums, k):
    result = []
    path = []

    def go(i, total):
        if total == k:
            result.append(list(path))
            return
        if total > k:
            return
        for j in range(i, len(nums)):
            path.append(nums[j])
            go(j + 1, total + nums[j])
            path.pop()

    go(0, 0)
    return sorted(result)
