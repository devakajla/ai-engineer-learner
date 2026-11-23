def rotate(items, k):
    if not items:
        return []
    k = k % len(items)
    return items[-k:] + items[:-k] if k else items[:]
