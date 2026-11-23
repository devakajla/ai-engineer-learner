def subsets(nums):
    result = []
    current = []

    def go(i):
        if i == len(nums):
            result.append(list(current))
            return
        go(i + 1)
        current.append(nums[i])
        go(i + 1)
        current.pop()

    go(0)
    return result
