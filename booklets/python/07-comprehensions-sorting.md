# 7. Comprehensions and sorting

Python has a short, readable way to build a new list from an old one. It is called a **comprehension**. It replaces the "make an empty list, loop, append" pattern with one line. Together with sorting, it is how most Python data work is written.

## The old way and the short way

Goal: the squares of 0 to 4.

```python
squares = []
for n in range(5):
    squares.append(n * n)
print(squares)
# -> [0, 1, 4, 9, 16]
```

The same with a **list comprehension**:

```python
squares = [n * n for n in range(5)]
print(squares)
# -> [0, 1, 4, 9, 16]
```

Read it like English: "give me `n * n` **for** each `n` **in** `range(5)`". The shape is `[what_to_keep  for  item  in  source]`. It produces a new list and leaves the source alone.

@@ flow | Figure 7.1: the three parts of a comprehension.
for n in range(5)|where items come from|blue -> if n % 2 == 0|optional filter|yellow -> n * n|what goes in the new list|green
@@ end

## Adding a filter

Add `if` at the end to keep only some items:

```python
print([n for n in range(10) if n % 2 == 0])
# -> [0, 2, 4, 6, 8]
```

Careful with the position. An `if` **at the end** *filters* (drops items). An `if ... else` **at the front** *chooses a value* for every item:

```python
print(["even" if n % 2 == 0 else "odd" for n in range(3)])
# -> ['even', 'odd', 'even']
```

## Sets and dicts too

Change the brackets and you change the result:

```python
print({word: len(word) for word in ["a", "bb"]})
# -> {'a': 1, 'bb': 2}
print({c for c in "hello"})
# -> {'h', 'o', 'e', 'l'}
```

(Set order is not promised, so yours may differ.) With `key: value` before `for`, you get a **dict comprehension**.

## Two loops in one

```python
print([(x, y) for x in range(2) for y in "ab"])
# -> [(0, 'a'), (0, 'b'), (1, 'a'), (1, 'b')]
```

The loops nest in the same order you would write them with normal `for` statements: the first `for` is the outer loop. Two loops are fine. Beyond that, write a normal loop. **Readability wins.**

## Generator expressions: the lazy cousin

Use round brackets and Python does **not** build the whole list. It makes a **generator** that produces one value at a time when asked.

```python
total = sum(n * n for n in range(1_000_000))
print(total)
# -> 333332833333500000
```

This never holds a million numbers in memory. For a sum, a maximum or a loop that only goes through the data once, a generator expression is better than a list. Chapter 10 explains how they work.

## Sorting

`sorted(items)` returns a new sorted list. It works on any group of items that can be compared:

```python
print(sorted([3, 1, 2]), sorted([3, 1, 2], reverse=True))
# -> [1, 2, 3] [3, 2, 1]
```

### Sorting by a rule: `key`

Often you do not sort the items themselves, but sort **by some property**. Give a function to `key=`. Python calls it once per item and sorts by the results.

```python
people = [{"n": "A", "age": 30}, {"n": "B", "age": 20}]
print(sorted(people, key=lambda p: p["age"]))
# -> [{'n': 'B', 'age': 20}, {'n': 'A', 'age': 30}]
print(sorted(["b", "A", "c"]))
# -> ['A', 'b', 'c']
```

Notice that normal text sorting puts capital letters first (`A` before `b`) because it compares character codes. For a case-blind sort use `key=str.lower`.

### Sorting by several fields

Return a **tuple** from the key. Python compares the first value, and uses the next only when the first is tied. A minus sign flips the order for numbers:

```python
data = [("a", 2), ("b", 1), ("c", 2)]
print(sorted(data, key=lambda t: (-t[1], t[0])))
# -> [('a', 2), ('c', 2), ('b', 1)]
```

Read the key as: "highest number first, and for equal numbers, alphabetical by letter."

Sorting is **stable**: items that compare equal keep their original relative order. That is what makes multi-step sorting predictable.

## Helpers that pair well

```python
print(any([0, 1]), all([1, 0]))
# -> True False
print(list(map(str, [1, 2])), list(filter(None, [0, 1, "", 2])))
# -> ['1', '2'] [1, 2]
```

`any` asks "is at least one true?" and `all` asks "are all true?". `map` applies a function to each item and `filter` keeps the truthy ones. In modern Python, a comprehension is usually clearer than `map` and `filter`, but you will see both in other people's code.

::: {.box .checkpoint}
**Checkpoint:** you can rewrite any "empty list, loop, append" as a comprehension, explain filter-`if` vs value-`if/else`, and sort a list of dicts by two fields.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Cramming complex logic into one comprehension. If it needs a second thought, use a loop.
- Using a comprehension only for its side effect (like `print`). Use a normal loop.
- Putting the `if ... else` at the end (a syntax error). The `else` form goes at the front.
- Building a huge list when a generator expression would do.
- Forgetting that `sorted` returns a new list and `list.sort()` returns `None`.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: List comprehension vs generator expression?** A list comprehension builds everything in memory at once. A generator expression produces items lazily, one at a time.

**Q: Is Python's sort stable?** Yes. Equal items keep their original order.

**Q: How do you sort by two criteria?** Return a tuple from `key`, and negate numbers for descending order.

**Q: How does `sorted` differ from `.sort()`?** `sorted` returns a new list from any iterable. `.sort()` changes a list in place and returns `None`.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. From `[1, 2, 3, 4, 5, 6]`, build the list of squares of the **odd** numbers.
2. Turn `["  a ", "b  "]` into `["a", "b"]` with a comprehension and `strip`.
3. Build a dict from words to their lengths for `"the quick brown fox".split()`.
4. Sort a list of words by length, and by alphabet when the length ties.
5. Sort a list of dicts `{"name": ..., "score": ...}` by score, highest first.
6. Flatten `[[1, 2], [3], [4, 5]]` into `[1, 2, 3, 4, 5]` with a two-loop comprehension.
7. **Think:** when would you pick `sum(x for ...)` over `sum([x for ...])`?
:::
