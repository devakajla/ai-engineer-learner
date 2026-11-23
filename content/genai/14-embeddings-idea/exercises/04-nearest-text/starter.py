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


# Your task:
def nearest_text(query, texts, vocab):
    ...
