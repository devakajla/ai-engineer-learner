def group_by_length(words):
    groups = {}
    for w in words:
        groups.setdefault(len(w), []).append(w)
    return groups
