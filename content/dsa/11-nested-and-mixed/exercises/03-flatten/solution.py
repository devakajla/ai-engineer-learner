def flatten(nested):
    flat = []
    for inner in nested:
        for x in inner:
            flat.append(x)
    return flat
