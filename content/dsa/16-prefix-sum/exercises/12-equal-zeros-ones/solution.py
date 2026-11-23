def equal_zeros_ones(nums):
    first = {0: -1}
    total = 0
    best = 0
    for i, x in enumerate(nums):
        total += 1 if x == 1 else -1
        if total in first:
            best = max(best, i - first[total])
        else:
            first[total] = i
    return best
