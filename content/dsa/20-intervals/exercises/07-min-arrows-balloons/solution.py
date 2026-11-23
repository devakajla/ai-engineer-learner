def min_arrows(balloons):
    arrows = 0
    last = None
    for end, start in sorted((e, s) for s, e in balloons):
        if last is None or start > last:
            arrows += 1
            last = end
    return arrows
