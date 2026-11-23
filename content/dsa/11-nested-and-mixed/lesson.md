---
title: "Nested and mixed structures"
summary: "Lists of lists, lists of dicts, sorting with a key, and list comprehensions."
plan_ids: []
---

Real data is nested: a grid is a list of lists, a set of records is a list of dicts. You already know each piece. Now combine them.

## List of lists (a grid)

```python
grid = [
    [1, 2, 3],
    [4, 5, 6],
]
print(grid[1][2])      # -> 6      row 1, column 2
print(len(grid))       # -> 2      rows
print(len(grid[0]))    # -> 3      columns
```

Loop over every cell:

```python
for r in range(len(grid)):
    for c in range(len(grid[r])):
        print(grid[r][c], end=" ")
# -> 1 2 3 4 5 6
```

Or loop over rows directly:

```python
for row in grid:
    print(sum(row))
# -> 6
# -> 15
```

> Build a new grid with a loop, not `[[0] * 3] * 2`. That makes both rows the **same** list.

```python
rows, cols = 2, 3
blank = []
for _ in range(rows):
    blank.append([0] * cols)
print(blank)   # -> [[0, 0, 0], [0, 0, 0]]
```

## List of dicts (records)

```python
students = [
    {"name": "Asha", "score": 80},
    {"name": "Dev", "score": 95},
]
for s in students:
    print(s["name"], s["score"])
# -> Asha 80
# -> Dev 95
```

## Sorting with `key`

`sorted(items, key=f)` sorts by the value `f(item)`.

```python
words = ["pear", "fig", "banana"]
print(sorted(words, key=len))    # -> ['fig', 'pear', 'banana']

def by_score(student):
    return student["score"]

print(sorted(students, key=by_score)[0]["name"])   # -> Asha
print(sorted(students, key=by_score, reverse=True)[0]["name"])   # -> Dev
```

**Sort by two things:** return a tuple. For "score high to low, then name A to Z" negate the score:

```python
def rank_key(student):
    return (-student["score"], student["name"])
```

## List comprehensions

A short way to build a list:

```python
print([n * n for n in range(1, 5)])         # -> [1, 4, 9, 16]
print([n for n in [1, 2, 3, 4] if n % 2 == 0])   # -> [2, 4]
print([row[0] for row in [[1, 2], [3, 4]]])      # -> [1, 3]
```

Same as a loop with `append`. Use whichever is clearer.

## Flatten with nested loops

```python
nested = [[1, 2], [3], [4, 5]]
flat = []
for row in nested:
    for x in row:
        flat.append(x)
print(flat)   # -> [1, 2, 3, 4, 5]
```

## Common mistakes

- `[[0] * 3] * 2`: rows share one list.
- Mixing up `grid[r][c]` order: row first, then column.
- Sorting records by a missing key (`KeyError`).
- Forgetting `key=` expects a function, not a call: `key=len`, not `key=len()`.

## Summary

- Grid: `grid[row][col]`; build rows with a loop.
- Records: list of dicts, read with `s["name"]`.
- `sorted(items, key=f, reverse=...)`; tuple keys for multi-level sort.
- Comprehension: `[expr for x in items if cond]`.
- Reference: `reference/comprehensions-and-sorting.md`.
