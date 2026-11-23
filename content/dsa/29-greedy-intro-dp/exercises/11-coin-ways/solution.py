def coin_ways(coins, amount):
    ways = [1] + [0] * amount
    for coin in coins:
        for a in range(coin, amount + 1):
            ways[a] += ways[a - coin]
    return ways[amount]
