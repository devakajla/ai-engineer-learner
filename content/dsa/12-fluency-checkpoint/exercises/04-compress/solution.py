def compress(s):
    if not s:
        return ""
    out = ""
    current = s[0]
    count = 0
    for ch in s:
        if ch == current:
            count += 1
        else:
            out += current + str(count)
            current = ch
            count = 1
    out += current + str(count)
    return out
