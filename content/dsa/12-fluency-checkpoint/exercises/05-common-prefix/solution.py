def common_prefix(words):
    if not words:
        return ""
    first = words[0]
    for i in range(len(first)):
        for w in words:
            if i >= len(w) or w[i] != first[i]:
                return first[:i]
    return first
