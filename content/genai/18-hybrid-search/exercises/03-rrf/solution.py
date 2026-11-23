def reciprocal_rank_fusion(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1 / (k + rank)
    pairs = list(scores.items())
    return sorted(pairs, key=pair_score, reverse=True)


def pair_score(pair):
    return pair[1]
