def split_first(items):
    if not items:
        return None, []
    first, *rest = items
    return first, rest
