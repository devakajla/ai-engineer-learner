def max_points(cards, k):
    size = len(cards) - k
    total = sum(cards)
    window = sum(cards[:size])
    smallest = window
    for i in range(size, len(cards)):
        window += cards[i] - cards[i - size]
        smallest = min(smallest, window)
    return total - smallest
