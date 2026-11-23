# Given from earlier exercises. Do not change these.
def recall(store, user_id, query, k=3):
    words = set(query.lower().split())
    scored = []
    for fact in store.get(user_id, []):
        score = len(words & set(fact.lower().split()))
        if score > 0:
            scored.append((score, fact))
    scored.sort(key=lambda pair: -pair[0])
    return [fact for _, fact in scored[:k]]


def size(messages):
    return sum(len(m["content"]) for m in messages)


# Your task:
def build_context(system, store, user_id, history, question, max_chars):
    facts = recall(store, user_id, question)
    messages = [{"role": "system", "content": system}]
    if facts:
        messages.append({"role": "system", "content": "Known facts about the user:\n- " + "\n- ".join(facts)})
    kept = list(history)
    tail = [{"role": "user", "content": question}]
    while kept and size(messages + kept + tail) > max_chars:
        kept.pop(0)
    return messages + kept + tail
