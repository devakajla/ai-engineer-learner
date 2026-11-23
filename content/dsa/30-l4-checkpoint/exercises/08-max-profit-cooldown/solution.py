def max_profit_cooldown(prices):
    hold = float("-inf")
    sold = 0
    rest = 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return max(sold, rest)
