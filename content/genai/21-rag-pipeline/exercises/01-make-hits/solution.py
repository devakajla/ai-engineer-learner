# Given from earlier exercises. Do not change these.
def hit_score(hit):
    return hit["score"]


def make_hits(chunks, scores, k, min_score=0.0):
    if k <= 0:
        return []
    pairs = []
    for chunk, score in zip(chunks, scores):
        hit = dict(chunk)
        hit["score"] = score
        pairs.append(hit)
    pairs = sorted(pairs, key=hit_score, reverse=True)
    return [hit for hit in pairs[:k] if hit["score"] >= min_score]
