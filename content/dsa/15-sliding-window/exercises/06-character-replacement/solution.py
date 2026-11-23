def character_replacement(s, k):
    counts = {}
    lo = 0
    best = 0
    for hi, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        while (hi - lo + 1) - max(counts.values()) > k:
            counts[s[lo]] -= 1
            lo += 1
        best = max(best, hi - lo + 1)
    return best
