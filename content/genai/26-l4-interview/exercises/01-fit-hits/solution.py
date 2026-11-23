def fit_hits(hits, max_words):
    chosen = []
    used = 0
    for hit in hits:
        words = len(hit["text"].split())
        if used + words > max_words:
            break
        chosen.append(hit)
        used += words
    return chosen
