def min_window(s, t):
    if not t:
        return ""
    need = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1
    missing = len(t)
    lo = 0
    best_start, best_len = 0, len(s) + 1
    for hi, ch in enumerate(s):
        if need.get(ch, 0) > 0:
            missing -= 1
        need[ch] = need.get(ch, 0) - 1
        while missing == 0:
            if hi - lo + 1 < best_len:
                best_start, best_len = lo, hi - lo + 1
            left = s[lo]
            need[left] += 1
            if need[left] > 0:
                missing += 1
            lo += 1
    return "" if best_len > len(s) else s[best_start:best_start + best_len]
