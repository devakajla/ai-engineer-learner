# Given from earlier exercises. Do not change these.
def by_rerank(hit):
    return hit["rerank_score"]


def rerank(score_fn, question, hits, top_n):
    if top_n <= 0:
        return []
    scored = []
    for hit in hits:
        new_hit = dict(hit)
        new_hit["rerank_score"] = score_fn(question, hit["text"])
        scored.append(new_hit)
    scored = sorted(scored, key=by_rerank, reverse=True)
    return scored[:top_n]
