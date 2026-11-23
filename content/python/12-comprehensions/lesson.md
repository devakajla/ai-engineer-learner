---
title: Comprehensions
summary: Build a list, set or dict in one short line, and know when a plain loop is the better choice.
plan_ids: []
---

A **comprehension** builds a new collection from another one in a single line. You already know the long way: make an empty list, loop, and `append`. A comprehension does the same job in one short, readable line.

## List comprehension

Here is the long way, and then the short way. Both build the squares of 0 to 4:

```python
# the loop way
squares = []
for n in range(5):
    squares.append(n * n)

# the comprehension way
squares = [n * n for n in range(5)]
print(squares)   # -> [0, 1, 4, 9, 16]
```

The form is `[expression for item in iterable]`. Read it out loud: "give me `expression` for each `item` in `iterable`".

## Keep only some items (a filter)

Add an `if` at the **end** to keep only the items that pass the test:

```python
nums = [1, 2, 3, 4, 5, 6]
evens = [n for n in nums if n % 2 == 0]
print(evens)   # -> [2, 4, 6]
```

You can change the items and filter them at the same time. Here is a step-by-step example: triple every number that is bigger than 10.

1. Decide the loop: `for n in nums`.
2. Decide the filter: `if n > 10`.
3. Decide what to give back for each item: `n * 3`.
4. Put them together: `[n * 3 for n in nums if n > 10]`.

```python
nums = [4, 12, 7, 20]
print([n * 3 for n in nums if n > 10])   # -> [36, 60]
```

Another one:

```python
words = ["apple", "fig", "banana"]
lengths = [len(w) for w in words if len(w) > 3]
print(lengths)   # -> [5, 6]
```

## Change items with `if` / `else`

If you want to **change** every item (not drop some), the `if ... else ...` goes at the **front**:

```python
nums = [1, 2, 3, 4]
labels = ["even" if n % 2 == 0 else "odd" for n in nums]
print(labels)   # -> ['odd', 'even', 'odd', 'even']
```

A way to remember it:

- A filter `if` (to drop items) goes at the **end**.
- A choice `if ... else` (to change items) goes at the **front**.

## Two loops in one

You can use two `for` parts. They read in the same order as nested loops.

```python
matrix = [[1, 2], [3, 4], [5, 6]]
flat = [n for row in matrix for n in row]
print(flat)    # -> [1, 2, 3, 4, 5, 6]
```

Read it as: "for each `row` in `matrix`, for each `n` in `row`, give me `n`". You can add a filter at the end, too:

```python
matrix = [[1, -2], [3, -4]]
print([n for row in matrix for n in row if n > 0])   # -> [1, 3]
```

Another example with pairs:

```python
pairs = [(x, y) for x in [1, 2] for y in ["a", "b"]]
print(pairs)   # -> [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]
```

## Set and dict comprehensions

With curly braces you can build a set or a dict.

```python
words = ["a", "bb", "a", "cc"]

unique_lengths = {len(w) for w in words}      # a set (one expression)
print(unique_lengths)                         # -> {1, 2}

lengths = {w: len(w) for w in words}          # a dict (key: value)
print(lengths)                                # -> {'a': 1, 'bb': 2, 'cc': 2}

price = {"apple": 3, "pear": 5}
doubled = {k: v * 2 for k, v in price.items()}
print(doubled)   # -> {'apple': 6, 'pear': 10}
```

## Generator expressions (a first look)

With round brackets you get a **generator expression**. It does not build a list. It makes one item at a time, so it uses almost no memory. It works nicely inside `sum`, `max`, `any` and `all`:

```python
total = sum(n * n for n in range(1000))
has_negative = any(n < 0 for n in [3, -1, 5])      # -> True
all_short = all(len(w) < 5 for w in ["a", "bb"])   # -> True
```

You will learn generators fully in Level 2.

## When not to use a comprehension

If it needs more than one `if`, or it does not fit in a line or two, use a normal loop. **Readability wins.**

```python
# too clever: use a loop instead
result = [x * y for x in range(10) if x % 2 for y in range(10) if y % 3]
```

Also, do not use a comprehension only for its side effects (like `print`). It builds a list that you never use.

## A little deeper (optional)

- The loop variable of a comprehension does **not** leak outside it in Python 3. After `[n for n in nums]`, the name `n` is not changed.
- `sum([n * n for n in range(10**6)])` builds a list of a million numbers first. `sum(n * n for n in range(10**6))` does not. Prefer the second.

## Common mistakes

- Putting the filter in the wrong place. `[x if x > 0 for x in nums]` is a `SyntaxError`, because an `if` at the front needs an `else`.
- Writing very long comprehensions that nobody can read.
- Using a list comprehension when a generator expression would do (inside `sum`, `any`, `all`).

## Summary

- `[expr for x in items]`, `[expr for x in items if cond]` and `[a if cond else b for x in items]`.
- Many `for` parts read like nested loops, left to right.
- `{expr for ...}` builds a set. `{k: v for ...}` builds a dict.
- `(expr for x in items)` is a lazy generator, good inside `sum`, `any` and `all`.
- Use a plain loop when the comprehension gets hard to read.
