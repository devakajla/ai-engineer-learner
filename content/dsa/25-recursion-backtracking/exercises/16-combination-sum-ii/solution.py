def combination_sum2(candidates, target):
    c = sorted(candidates)
    result = []
    current = []

    def go(start, remaining):
        if remaining == 0:
            result.append(list(current))
            return
        for i in range(start, len(c)):
            if i > start and c[i] == c[i - 1]:
                continue
            if c[i] > remaining:
                break
            current.append(c[i])
            go(i + 1, remaining - c[i])
            current.pop()

    go(0, target)
    return result
