def permutations(nums):
    result = []
    current = []
    used = [False] * len(nums)

    def go():
        if len(current) == len(nums):
            result.append(list(current))
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            current.append(nums[i])
            go()
            current.pop()
            used[i] = False

    go()
    return result
