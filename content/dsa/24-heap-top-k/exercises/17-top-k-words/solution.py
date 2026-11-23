import heapq


def top_k_words(words, k):
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    h = [(-c, w) for w, c in counts.items()]
    heapq.heapify(h)
    return [heapq.heappop(h)[1] for _ in range(k)]
