import math


def ndcg_at_k(relevances, k):
    top = relevances[:k] if k > 0 else []
    dcg = sum(rel / math.log2(position + 1) for position, rel in enumerate(top, start=1))
    ideal = sorted(relevances, reverse=True)[:k] if k > 0 else []
    idcg = sum(rel / math.log2(position + 1) for position, rel in enumerate(ideal, start=1))
    if idcg == 0:
        return 0.0
    return dcg / idcg
