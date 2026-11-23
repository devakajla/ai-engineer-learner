# Given from earlier exercises. Do not change these.
def pair_score(pair):
    return pair[1]


def reciprocal_rank_fusion(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1 / (k + rank)
    pairs = list(scores.items())
    return sorted(pairs, key=pair_score, reverse=True)


def retrieve_multi(retrieve, queries, k):
    rankings = []
    by_id = {}
    for query in queries:
        hits = retrieve(query, k)
        rankings.append([hit["id"] for hit in hits])
        for hit in hits:
            if hit["id"] not in by_id:
                by_id[hit["id"]] = hit
    fused = reciprocal_rank_fusion(rankings)
    return [by_id[item] for item, score in fused[:k]]
