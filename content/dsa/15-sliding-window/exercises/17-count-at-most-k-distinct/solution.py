def count_at_most_k_distinct(s, k):
    counts = {}
    lo = 0
    total = 0
    for hi, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        while len(counts) > k:
            counts[s[lo]] -= 1
            if counts[s[lo]] == 0:
                del counts[s[lo]]
            lo += 1
        total += hi - lo + 1
    return total
