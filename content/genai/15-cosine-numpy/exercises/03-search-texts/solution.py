import numpy as np


def cosine_scores(query_vector, doc_vectors):
    """One cosine score per document vector. A zero vector scores 0.0."""
    docs = np.array(doc_vectors, dtype=float)
    q = np.array(query_vector, dtype=float)
    lengths = np.linalg.norm(docs, axis=1) * np.linalg.norm(q)
    dots = docs @ q
    scores = np.zeros(len(docs))
    nonzero = lengths != 0
    scores[nonzero] = dots[nonzero] / lengths[nonzero]
    return [float(s) for s in scores]


def search_texts(embed, query, texts, k=3):
    if k <= 0 or not texts:
        return []
    doc_vectors = embed(texts)
    query_vector = embed([query])[0]
    scores = cosine_scores(query_vector, doc_vectors)
    order = np.argsort(-np.array(scores), kind="stable")[:k]
    return [(texts[i], scores[i]) for i in order]
