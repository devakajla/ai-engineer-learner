def max_profit(prices):
    lowest = None
    best = 0
    for p in prices:
        if lowest is None or p < lowest:
            lowest = p
        best = max(best, p - lowest)
    return best
