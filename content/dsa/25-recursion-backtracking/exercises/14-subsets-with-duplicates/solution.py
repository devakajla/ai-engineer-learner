def subsets_with_dup(nums):
    nums = sorted(nums)
    result = []
    current = []

    def go(start):
        result.append(list(current))
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            current.append(nums[i])
            go(i + 1)
            current.pop()

    go(0)
    return result
