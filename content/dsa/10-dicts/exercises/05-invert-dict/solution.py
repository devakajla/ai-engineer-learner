def invert_dict(d):
    result = {}
    for k, v in d.items():
        result[v] = k
    return result
