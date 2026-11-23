# Lists

Ordered, changeable. Index from 0.

| Method / built-in | Does | Changes list? | Returns |
| --- | --- | --- | --- |
| `append(x)` | add at end | yes | `None` |
| `insert(i, x)` | add at index | yes | `None` |
| `remove(x)` | remove first value x | yes | `None` |
| `pop()` / `pop(i)` | remove and return | yes | item |
| `sort()` | sort in place | yes | `None` |
| `sorted(l)` | sorted copy | no | new list |
| `reverse()` | reverse in place | yes | `None` |
| `l[::-1]` | reversed copy | no | new list |
| `l.count(x)`, `l.index(x)` | count / position | no | int |
| `len sum min max` | basics | no | value |
| `x in l` | membership (scans) | no | bool |
| `l.copy()` / `l[:]` | shallow copy | no | new list |

## Index and slice
```python
nums = [10, 20, 30, 40, 50]
print(nums[0], nums[-1], nums[1:3], nums[::-1])   # -> 10 50 [20, 30] [50, 40, 30, 20, 10]
```
**Gotcha:** `IndexError` for an out-of-range index; slices never raise.

## `append`, `insert`, `remove`, `pop`
```python
items = [1, 2, 3]
items.append(4)
items.insert(0, 0)
items.remove(2)
last = items.pop()
print(items, last)   # -> [0, 1, 3] 4
```
**Gotcha:** they return `None`. `x = x.append(1)` makes `x` `None`. `pop(0)` and `insert(0, ...)` are slow on long lists (all items shift). `remove` raises `ValueError` if missing.

## `sort` vs `sorted`
```python
a = [3, 1, 2]
print(sorted(a), a)   # -> [1, 2, 3] [3, 1, 2]
a.sort()
print(a)              # -> [1, 2, 3]
```
Options: `reverse=True`, `key=...` (see `comprehensions-and-sorting.md`).

## Copying
```python
a = [1, 2]
b = a          # same list
c = a[:]       # new list
b.append(3)
print(a, c)    # -> [1, 2, 3] [1, 2]
```
**Gotcha:** copies are shallow. Inner lists are still shared.

## `enumerate`
```python
for i, v in enumerate(["a", "b"]):
    print(i, v)   # -> 0 a / 1 b
```

## `x in list` cost
`in` scans item by item. For many lookups, build a `set` first.

## Patterns on lists
Best so far, running total, build a new list, two indexes (`i`, `j`). See `functions-and-patterns.md`. Lesson: `dsa/07-lists`.
