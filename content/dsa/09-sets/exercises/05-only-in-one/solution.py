def only_in_one(a, b):
    return sorted(set(a) ^ set(b))
