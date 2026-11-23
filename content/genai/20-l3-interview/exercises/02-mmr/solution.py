def mmr(query_sims, doc_sims, k, lam=0.5):
    remaining = list(range(len(query_sims)))
    picked = []
    while remaining and len(picked) < k:
        best = None
        best_score = None
        for i in remaining:
            penalty = max((doc_sims[i][j] for j in picked), default=0)
            score = lam * query_sims[i] - (1 - lam) * penalty
            if best_score is None or score > best_score:
                best = i
                best_score = score
        picked.append(best)
        remaining.remove(best)
    return picked
