def count_pairs(text):
    words = text.lower().split()
    counts = {}
    for i in range(len(words) - 1):
        first = words[i]
        second = words[i + 1]
        if first not in counts:
            counts[first] = {}
        counts[first][second] = counts[first].get(second, 0) + 1
    return counts
