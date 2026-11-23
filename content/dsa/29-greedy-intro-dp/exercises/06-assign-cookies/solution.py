def content_children(greed, sizes):
    greed = sorted(greed)
    child = 0
    for size in sorted(sizes):
        if child < len(greed) and size >= greed[child]:
            child += 1
    return child
