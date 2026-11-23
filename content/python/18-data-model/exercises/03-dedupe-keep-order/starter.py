def dedupe(items):
    for x in items:
        while items.count(x) > 1:
            items.remove(x)
    return items
