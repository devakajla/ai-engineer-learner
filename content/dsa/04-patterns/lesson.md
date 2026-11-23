---
title: "Pattern problems"
summary: "Nested loops and string building: print shapes like triangles and pyramids by returning a list of rows."
plan_ids: []
---

Pattern problems look silly but they train one important skill: **nested loops**, and thinking about "row number" vs "column number".

In this track, a pattern function **returns a list of strings**, one string per row. That way the tests can check it. To see it, print the rows yourself.

## Repeat a string

`"*" * 3` gives `"***"`. Spaces work too: `" " * 2 + "*"`.

```python
print("*" * 3)          # -> ***
print(" " * 2 + "*")    # -> "  *"
```

## One row at a time

Most patterns need no inner loop. For each row `i`, work out **how many spaces** and **how many stars**, then build the row with `*`.

```python
def right_triangle(n):
    rows = []
    for i in range(1, n + 1):
        rows.append("*" * i)
    return rows

for row in right_triangle(3):
    print(row)
# -> *
# -> **
# -> ***
```

## Find the formula on paper

For a pyramid with 3 rows:

```text
row 1:   *      2 spaces, 1 star
row 2:  ***     1 space,  3 stars
row 3: *****    0 spaces, 5 stars
```

For row `i` (starting at 1): spaces = `n - i`, stars = `2 * i - 1`.

```python
def pyramid(n):
    rows = []
    for i in range(1, n + 1):
        rows.append(" " * (n - i) + "*" * (2 * i - 1))
    return rows
```

> Always fill a small table: row number, spaces, stars. The formula appears from the table.

## Nested loops

When a row has different characters (like numbers), use an inner loop:

```python
def number_triangle(n):
    rows = []
    for i in range(1, n + 1):
        row = ""
        for j in range(1, i + 1):
            row += str(j)
        rows.append(row)
    return rows

print(number_triangle(3))   # -> ['1', '12', '123']
```

Outer loop = rows. Inner loop = columns in that row.

## `str.join`

Join pieces into one string:

```python
print(" ".join(["a", "b", "c"]))   # -> a b c
print("".join(["1", "2"]))         # -> 12
```

## Common mistakes

- Off-by-one in `range`: rows start at 1, `range(1, n + 1)`.
- Mixing numbers and strings: `str(j)` before adding to a string.
- Trailing spaces. The tests compare exact strings.
- Printing instead of returning the list.

## Summary

- Return a list of row strings.
- Build each row from counts: `" " * spaces + "*" * stars`.
- Fill a table (row, spaces, stars) to find the formula.
- Inner loop only when the characters change inside a row.
