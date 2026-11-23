# Tuples and unpacking

A tuple is a fixed group of values. Immutable and hashable (if its items are).

| Tool | Does |
| --- | --- |
| `(a, b)` / `a, b` | make a tuple |
| `(a,)` | one-item tuple (comma needed) |
| `x, y = pair` | unpack |
| `a, b = b, a` | swap |
| `first, *rest = items` | star unpack |
| `zip(a, b)` | pair items of two sequences |
| `tuple(items)` | convert |

## Unpack and swap
```python
x, y = (3, 4)
a, b = 1, 2
a, b = b, a
print(x, y, a, b)   # -> 3 4 2 1
```
**Theory:** the right side is built first, then assigned. That is why the swap works.
**Gotcha:** wrong count raises `ValueError: too many values to unpack`.

## Return several values
```python
def min_max(nums):
    return min(nums), max(nums)

low, high = min_max([4, 1, 9])
print(low, high)   # -> 1 9
```

## Star unpacking
```python
first, *rest = [1, 2, 3]
print(first, rest)   # -> 1 [2, 3]
```

## `zip`
```python
print(list(zip([1, 2, 3], ["a", "b"])))   # -> [(1, 'a'), (2, 'b')]
```
**Gotcha:** stops at the shorter input. `zip` itself is lazy; wrap in `list(...)` to see it.

## As keys
Tuples can be dict keys and set members; lists cannot.
```python
seen = {(1, 2)}
print((1, 2) in seen)   # -> True
```
Lesson: `dsa/08-tuples-unpacking`.
