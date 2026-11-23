"""Keyword search with BM25. Pure functions, no model calls."""

import math

PUNCTUATION = ".,;:!?()\"'`"


def tokenize(text):
    """Lowercase words. Punctuation is stripped from the ends of each word, the inside is kept."""
    words = []
    for word in text.lower().split():
        word = word.strip(PUNCTUATION)
        if word:
            words.append(word)
    return words


def bm25_scores(query, docs, k1=1.5, b=0.75):
    """One BM25 score per document text, in the same order."""
    if not docs:
        return []
    tokenized = [tokenize(doc) for doc in docs]
    n = len(docs)
    avg_length = sum(len(tokens) for tokens in tokenized) / n
    if avg_length == 0:
        return [0.0] * n
    scores = [0.0] * n
    for term in dict.fromkeys(tokenize(query)):
        df = 0
        for tokens in tokenized:
            if term in tokens:
                df += 1
        if df == 0:
            continue
        idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
        for i, tokens in enumerate(tokenized):
            tf = tokens.count(term)
            if tf == 0:
                continue
            norm = tf + k1 * (1 - b + b * len(tokens) / avg_length)
            scores[i] += idf * tf * (k1 + 1) / norm
    return scores


def rank_by_score(scores):
    """Indexes of the scores, best first, skipping zeros. Ties: lower index first."""
    pairs = [(-scores[i], i) for i in range(len(scores)) if scores[i] > 0]
    pairs.sort()
    return [i for _, i in pairs]
