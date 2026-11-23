import math


# Given from earlier exercises. Do not change these.
PUNCTUATION = ".,;:!?()\"'`"


def tokenize(text):
    words = []
    for word in text.lower().split():
        word = word.strip(PUNCTUATION)
        if word:
            words.append(word)
    return words


def bm25_scores(query, docs, k1=1.5, b=0.75):
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


def reciprocal_rank_fusion(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1 / (k + rank)
    pairs = list(scores.items())
    return sorted(pairs, key=pair_score, reverse=True)


def pair_score(pair):
    return pair[1]


def rank_indexes(scores):
    return sorted(range(len(scores)), key=scores.__getitem__, reverse=True)


# Your task:
def hybrid_search(query, docs, vector_scores, k=3):
    ...
