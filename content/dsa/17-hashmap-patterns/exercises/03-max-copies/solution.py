def max_copies(text, word):
    have = {}
    for ch in text:
        have[ch] = have.get(ch, 0) + 1
    need = {}
    for ch in word:
        need[ch] = need.get(ch, 0) + 1
    best = None
    for ch, n in need.items():
        copies = have.get(ch, 0) // n
        if best is None or copies < best:
            best = copies
    return best
