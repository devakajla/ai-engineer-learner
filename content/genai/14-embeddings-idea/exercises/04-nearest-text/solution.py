# Given from earlier exercises. Do not change these.
def toy_embed(text, vocab):
    words = [word.strip(".,!?") for word in text.lower().split()]
    counts = []
    for term in vocab:
        counts.append(words.count(term))
    return counts

def euclidean(a, b):
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    total = 0
    for x, y in zip(a, b):
        total += (x - y) ** 2
    return float(total ** 0.5)


def nearest_text(query, texts, vocab):
    if not texts:
        return None
    query_vector = toy_embed(query, vocab)
    best_text = None
    best_distance = None
    for text in texts:
        distance = euclidean(query_vector, toy_embed(text, vocab))
        if best_distance is None or distance < best_distance:
            best_text = text
            best_distance = distance
    return best_text
