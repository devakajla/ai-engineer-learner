def total_fruit(fruits):
    counts = {}
    lo = 0
    best = 0
    for hi, f in enumerate(fruits):
        counts[f] = counts.get(f, 0) + 1
        while len(counts) > 2:
            counts[fruits[lo]] -= 1
            if counts[fruits[lo]] == 0:
                del counts[fruits[lo]]
            lo += 1
        best = max(best, hi - lo + 1)
    return best
