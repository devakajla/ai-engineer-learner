def merge_add(a, b):
    result = dict(a)
    for k, v in b.items():
        result[k] = result.get(k, 0) + v
    return result
