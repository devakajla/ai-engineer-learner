---
title: "Recursion & backtracking"
summary: "A function that calls itself on a smaller problem; backtracking tries every choice and undoes it."
plan_ids: []
---

**Recursion** means a function calls itself on a smaller version of the same problem. Many hard-looking problems become short once you think: *what is the smallest case, and how does a big case use a smaller one?*

> Watch the intro video first. Exercises 01 to 09 have video segments.

## The two parts

Every recursive function needs:

1. **Base case**: the smallest input you can answer directly. Without it, the function never stops.
2. **Recursive case**: solve a smaller input and use its answer.

```python
def sum_list(nums):
    if not nums:                         # base case
        return 0
    return nums[0] + sum_list(nums[1:])  # smaller problem

print(sum_list([1, 2, 3]))   # -> 6
```

Python stops a runaway recursion after about 1000 calls (`RecursionError`). Good base cases and shrinking inputs prevent it.

## Think "trust the recursion"

Do not trace every call. Say: "If `sum_list(rest)` is correct, my line is correct." Check only the base case and one step.

## Memoization: do not repeat work

Plain Fibonacci calls the same `fib(k)` thousands of times. Remember results in a dict:

```python
def fib(n, memo=None):
    if memo is None:
        memo = {}
    if n < 2:
        return n
    if n not in memo:
        memo[n] = fib(n - 1, memo) + fib(n - 2, memo)
    return memo[n]

print(fib(40))   # -> 102334155
```

## Divide in half

`x^n = (x^(n//2))^2`, times `x` if `n` is odd. Only about log n calls.

## Backtracking: choose, explore, undo

Backtracking builds an answer step by step. At each step you try every choice, go deeper, and **undo** the choice when you come back.

```python
def subsets(nums):
    result, current = [], []

    def go(i):
        if i == len(nums):
            result.append(list(current))   # save a COPY
            return
        go(i + 1)                # skip nums[i]
        current.append(nums[i])  # choose
        go(i + 1)                # explore
        current.pop()            # undo

    go(0)
    return result

print(subsets([1, 2]))   # -> [[], [2], [1], [1, 2]]
```

The template:

```text
go(state):
    if state is complete: save a copy; return
    for each choice allowed now:
        make the choice
        go(next state)
        undo the choice
```

## Choosing the shape

| Problem | Choice at each step |
| --- | --- |
| Subsets | take or skip |
| Permutations | any unused item |
| Combinations | any item after the last chosen (start index) |
| Combination sum (reuse) | stay on the same index |
| Strings (parentheses, phone) | add one character with rules |
| Grid word search | one of 4 neighbours, mark and unmark the cell |

## Duplicates

Sort first. In a loop at the same depth, skip a number equal to the one before it: `if i > start and nums[i] == nums[i - 1]: continue`.

## Pruning

Stop early when the path cannot work: `remaining < 0`, `c[i] > remaining` (sorted), a queen already attacked. This cuts the search a lot.

## Common mistakes

- No base case, or a base case that is never reached.
- Saving `current` instead of `list(current)`: later changes alter the saved answer.
- Forgetting to **undo** the choice.
- Wrong skip rule for duplicates (`i > 0` instead of `i > start`).
- Using recursion where a loop is simpler.

## Interview corner

**Q: Time complexity of subsets?**
A: O(2^n) results, so O(n * 2^n) with copying.

**Q: What is backtracking?**
A: Depth-first search over choices: try, go deeper, undo.

**Q: Recursion vs memoization vs DP?**
A: Memoization keeps results of repeated calls (top-down DP). It turns exponential Fibonacci into O(n).

**Q: How do you avoid duplicate subsets in an input with repeats?**
A: Sort, and skip equal neighbours at the same level.

## Summary

- Base case + smaller problem. Trust the recursion.
- Backtracking: choose, explore, undo; save copies.
- Memoize repeated work; halve the problem when you can; prune dead ends.
- Cheat sheet: `reference/patterns.md`.
