def find_anagrams(s, p):
    k = len(p)
    need = {}
    for ch in p:
        need[ch] = need.get(ch, 0) + 1
    window = {}
    result = []
    for i, ch in enumerate(s):
        window[ch] = window.get(ch, 0) + 1
        if i >= k:
            old = s[i - k]
            window[old] -= 1
            if window[old] == 0:
                del window[old]
        if i >= k - 1 and window == need:
            result.append(i - k + 1)
    return result
