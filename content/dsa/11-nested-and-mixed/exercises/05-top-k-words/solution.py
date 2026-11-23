def top_k_words(text, k):
    counts = {}
    for w in text.lower().split():
        counts[w] = counts.get(w, 0) + 1
    pairs = []
    for w, c in counts.items():
        pairs.append((-c, w))
    pairs.sort()
    return [w for _, w in pairs[:k]]
