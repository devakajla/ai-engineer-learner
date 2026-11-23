def max_len_positive_product(nums):
    pos = neg = 0
    best = 0
    for x in nums:
        if x == 0:
            pos = neg = 0
        elif x > 0:
            pos, neg = pos + 1, (neg + 1 if neg else 0)
        else:
            pos, neg = (neg + 1 if neg else 0), pos + 1
        best = max(best, pos)
    return best
