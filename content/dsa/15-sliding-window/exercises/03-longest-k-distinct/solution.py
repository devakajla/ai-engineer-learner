def longest_k_distinct(s, k):
    counts = {}
    lo = 0
    best = 0
    for hi, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        while len(counts) > k:
            left = s[lo]
            counts[left] -= 1
            if counts[left] == 0:
                del counts[left]
            lo += 1
        best = max(best, hi - lo + 1)
    return best
