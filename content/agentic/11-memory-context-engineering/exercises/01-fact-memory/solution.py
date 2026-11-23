def save_fact(store, user_id, fact):
    facts = store.setdefault(user_id, [])
    if fact.strip().lower() in [f.lower() for f in facts]:
        return False
    facts.append(fact.strip())
    return True


def recall(store, user_id, query, k=3):
    words = set(query.lower().split())
    scored = []
    for fact in store.get(user_id, []):
        score = len(words & set(fact.lower().split()))
        if score > 0:
            scored.append((score, fact))
    scored.sort(key=lambda pair: -pair[0])
    return [fact for _, fact in scored[:k]]
