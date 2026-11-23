---
title: "Greedy & Intro to DP"
summary: "Two ways to optimise: make the best local choice (greedy), or remember sub-answers so you never solve the same problem twice (DP)."
plan_ids: []
---

Many problems ask for the **biggest**, **smallest**, **fewest** or **number of ways**. Two tools cover most of the easy and medium ones: **greedy** and **dynamic programming (DP)**.

> This lesson has no classes and no new library. It uses lists and loops only. Intro video: DP basics.

## Greedy: take the best choice now

A greedy algorithm makes the best-looking choice at each step and never looks back. It is fast and short, but it is only correct when a local best choice also leads to a global best. Test it on small cases (the exercises do this with a brute-force check).

Common greedy shapes:

- **Sort, then sweep.** Meetings: sort by end time and take every meeting that fits.

```python
meetings = [[1, 3], [2, 4], [3, 5]]
last_end, count = 0, 0
for end, start in sorted((end, start) for start, end in meetings):
    if start >= last_end:
        count += 1
        last_end = end
print(count)   # -> 2
```

- **Track the farthest reach.** Jump game: `reach = max(reach, i + nums[i])`.
- **Collect every gain.** Stocks with many trades: add each positive day-to-day rise.
- **Reset when it fails.** Gas station: when the tank goes negative, restart from the next station.

> Greedy can be wrong. Coins `[1, 3, 4]` and amount `6`: greedy takes `4 + 1 + 1` (3 coins), the best is `3 + 3` (2 coins). That problem needs DP.

## DP: remember sub-answers

DP fits when:

1. The problem breaks into **smaller versions of itself**.
2. The same smaller versions appear **again and again**.

Plain recursion repeats work. Climbing stairs with recursion is exponential:

```python
def ways(n):
    if n <= 1:
        return 1
    return ways(n - 1) + ways(n - 2)

print(ways(10))   # -> 89   (but ways(45) takes forever)
```

DP stores each answer once.

### Recipe

1. **State:** what does `dp[i]` mean, in words?
2. **Transition:** how does `dp[i]` come from smaller states?
3. **Base case:** the smallest states you know.
4. **Order and answer:** fill from small to big; say which cell is the answer.

### 1D DP: stairs and house robber

```python
def climb_stairs(n):
    prev, cur = 1, 1
    for _ in range(n - 1):
        prev, cur = cur, prev + cur
    return cur

print(climb_stairs(45))   # -> 1836311903
```

Take-or-skip: `best[i] = max(best[i-1], best[i-2] + nums[i])` (house robber). When `dp[i]` only needs the last two values, keep two variables.

### Coin change: DP over amounts

```python
def coin_change(coins, amount):
    inf = float("inf")
    best = [0] + [inf] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] + 1 < best[a]:
                best[a] = best[a - c] + 1
    return best[amount] if best[amount] != inf else -1

print(coin_change([1, 3, 4], 6))   # -> 2
```

To **count combinations**, put the coin loop **outside** (so order does not matter). To count orderings, put the amount loop outside.

### Knapsack: use each item once

```python
best = [0] * (capacity + 1)
for weight, value in zip(weights, values):
    for c in range(capacity, weight - 1, -1):      # backwards!
        best[c] = max(best[c], best[c - weight] + value)
```

Going **backwards** stops an item from being used twice. Subset sum and "split into equal halves" are the same idea with `True/False` instead of values.

### Subsequences: LIS and LCS

- **LIS:** `best[i]` = longest increasing subsequence **ending at** `i`; look at all `j < i` with a smaller value.
- **LCS:** a 2D table `dp[i][j]` for prefixes. Equal last characters: `dp[i-1][j-1] + 1`. Else the max of dropping one character from either string.

## Common mistakes

- Using greedy without checking a counter-example.
- A `dp[i]` with no clear meaning in words.
- Wrong base case (`best[0]`, empty strings).
- Knapsack loop in the wrong direction (item used many times).
- Coin loops swapped (counting orderings instead of combinations).
- Plain recursion with no memo on big inputs.

## Interview corner

**Q: How do you know DP applies?**
A: The answer builds from smaller overlapping subproblems, and you ask for a max, min, count or yes/no.

**Q: Greedy or DP?**
A: Try greedy first and look for a counter-example. If a local best choice can fail, use DP.

**Q: What is the time complexity of coin change?**
A: O(amount * number of coins).

**Q: Top-down vs bottom-up?**
A: Top-down is recursion plus a memo. Bottom-up fills a table in order. Same answers; bottom-up has no recursion depth limit.

## Summary

- Greedy: sort, sweep, keep the best local choice. Always test it.
- DP: state, transition, base case, answer.
- 1D DP (stairs, robber, coins), knapsack (backwards loop), subsequences (LIS, LCS).
- Cheat sheet: `reference/patterns.md`.
