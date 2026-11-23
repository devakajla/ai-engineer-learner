def combination_sum(candidates, target):
    result = []
    current = []

    def go(i, remaining):
        if remaining == 0:
            result.append(list(current))
            return
        if remaining < 0 or i == len(candidates):
            return
        current.append(candidates[i])
        go(i, remaining - candidates[i])
        current.pop()
        go(i + 1, remaining)

    go(0, target)
    return result
