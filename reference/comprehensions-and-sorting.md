# Comprehensions, sorting and nested data

## List comprehension
**Signature:** `[expr for x in items if cond]`
**Theory:** a compact loop that builds a list. The `if` part is optional.
```python
print([n * n for n in range(1, 5)])               # -> [1, 4, 9, 16]
print([n for n in [1, 2, 3, 4] if n % 2 == 0])    # -> [2, 4]
```
**Gotcha:** if it needs more than one idea, write a normal loop.

## `sorted(items, key=f, reverse=False)`
**Theory:** returns a new list ordered by `f(item)`. `f` is a function passed **without** calling it.
```python
print(sorted(["pear", "fig", "banana"], key=len))   # -> ['fig', 'pear', 'banana']
```
**Multi-level sort:** return a tuple. Negate numbers to reverse only one level.
```python
def rank_key(s):
    return (-s["score"], s["name"])
```

## Grid (list of lists)
```python
grid = [[1, 2, 3], [4, 5, 6]]
print(grid[1][2], len(grid), len(grid[0]))   # -> 6 2 3
```
Index order: `grid[row][col]`.
**Gotcha:** `[[0] * 3] * 2` makes both rows the same list. Build rows in a loop:
```python
blank = []
for _ in range(2):
    blank.append([0] * 3)
```

## Records (list of dicts)
```python
people = [{"n": "a", "age": 30}, {"n": "b", "age": 20}]
print([p["n"] for p in people])   # -> ['a', 'b']
```

## Flatten
```python
flat = []
for inner in [[1, 2], [3]]:
    for x in inner:
        flat.append(x)
print(flat)   # -> [1, 2, 3]
```
Lesson: `dsa/11-nested-and-mixed`.
