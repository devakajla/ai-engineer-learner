def toy_embed(text, vocab):
    words = [word.strip(".,!?") for word in text.lower().split()]
    counts = []
    for term in vocab:
        counts.append(words.count(term))
    return counts
