def common_items(a, b):
    return sorted(set(a) & set(b))


def dedupe_keep_order(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
