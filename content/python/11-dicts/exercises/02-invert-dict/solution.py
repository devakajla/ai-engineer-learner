def invert(d):
    result = {}
    for key, value in d.items():
        result[value] = key
    return result
