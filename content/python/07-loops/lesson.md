---
title: "Loops: while, for, range"
summary: Repeat work with while and for, stop or skip with break and continue, and use range, enumerate and zip.
plan_ids: []
---

A **loop** repeats code. Without loops you would write the same line 100 times. Python has two loops: `while` (repeat while a condition is true) and `for` (go through things one by one). You will use `for` most of the time.

## `while`

`while` repeats as long as its condition is true:

```python
n = 3
while n > 0:
    print(n)
    n -= 1
# -> 3
# -> 2
# -> 1
```

Something inside the loop must change the condition. If not, the loop runs forever.

## `for`

`for` takes each item of something (a string, a range, a list ...) one at a time. Something you can loop over is called an **iterable**.

```python
for ch in "abc":
    print(ch)
# -> a
# -> b
# -> c
```

Here `ch` is the name for the current item. It is a new item in each round.

A very common pattern is the **accumulator**: start with a value, then update it in each round.

```python
total = 0
for price in [10, 20, 5]:    # [10, 20, 5] is a list. You learn lists in lesson 8.
    total += price
print(total)   # -> 35
```

## `range`

`range(stop)` gives the numbers from 0 up to, but **not including**, `stop`:

```python
for i in range(3):
    print("hello", i)
# -> hello 0
# -> hello 1
# -> hello 2
```

You can give a start and a step too: `range(start, stop, step)`.

```python
list(range(4))           # -> [0, 1, 2, 3]
list(range(2, 6))        # -> [2, 3, 4, 5]
list(range(10, 0, -3))   # -> [10, 7, 4, 1]
```

(`list(...)` turns the numbers into a list so we can see them.)

Here is a step-by-step example. What is `1 * 2 * 3 * 4 * 5`?

1. Start with `result = 1`. (We start with 1, because multiplying by 1 changes nothing.)
2. Loop over the numbers `1` to `5`. Remember that `range(1, 6)` stops before 6.
3. In each round, multiply `result` by the number.

```python
result = 1
for i in range(1, 6):
    result *= i
print(result)   # -> 120
```

## Show on one line

`print` normally ends with a new line. Use `end=" "` to put a space instead:

```python
for i in range(3):
    print(i, end=" ")
# -> 0 1 2
```

## `break`, `continue` and `else`

- `break` leaves the loop completely.
- `continue` skips the rest of this round and goes to the next one.

```python
for n in [1, 2, 3, 4, 5]:
    if n == 2:
        continue        # skip 2
    if n == 4:
        break           # stop at 4
    print(n)
# -> 1
# -> 3
```

A loop can also have an `else` block. It runs only when the loop ended **without** a `break`:

```python
for n in [3, 5, 7]:
    if n % 2 == 0:
        print("found an even number")
        break
else:
    print("no even number")   # -> no even number
```

## `enumerate`: the position and the item

When you need the item **and** its position, use `enumerate`:

```python
names = ["Ada", "Linus", "Guido"]
for i, name in enumerate(names):
    print(i, name)
# -> 0 Ada
# -> 1 Linus
# -> 2 Guido

for i, name in enumerate(names, start=1):   # start counting at 1
    print(i, name)
# -> 1 Ada
# -> 2 Linus
# -> 3 Guido
```

Do not write `for i in range(len(names))` just to get the position. `enumerate` is cleaner.

## `zip`: two things at once

`zip` walks through two things together:

```python
names = ["Ada", "Linus"]
ages = [36, 55]
for name, age in zip(names, ages):
    print(name, age)
# -> Ada 36
# -> Linus 55
```

If one is shorter, `zip` stops when the shortest one ends:

```python
list(zip([1, 2, 3], ["a", "b"]))   # -> [(1, 'a'), (2, 'b')]
```

## Loops inside functions

In an exercise you often loop inside a function, and `return` once the loop has found the answer. A `return` inside a loop ends the loop and the function right away:

```python
def first_even(numbers):
    for n in numbers:
        if n % 2 == 0:
            return n      # stop here and give back n
    return None           # the loop ended and found nothing

first_even([3, 5, 8, 9])   # -> 8
```

## Remembering what you have seen

Sometimes the loop must remember earlier items. A **list** can do this (you will learn lists fully in lesson 8). Three things are enough for now:

```python
seen = []           # an empty list
seen.append("a")    # add an item at the end
"a" in seen         # -> True   is "a" in the list?
"z" in seen         # -> False
```

For example, here we find the first word that has a capital first letter and print each word we have already checked:

```python
checked = []
for word in ["go", "Run", "stop"]:
    if word[0].isupper():
        print("found", word)    # -> found Run
        break
    checked.append(word)
print(checked)                  # -> ['go']
```

## Common mistakes

- Off-by-one with `range`. `range(5)` is `0` to `4`, not `1` to `5`. For `1` to `5`, write `range(1, 6)`.
- Changing a list while you loop over it. This skips items. Build a new list instead.
- A `while` loop that never ends, because the variable is never updated.
- Using `range(len(x))` when `for item in x` or `enumerate(x)` is enough.
- Thinking loop `else` means "the loop failed". It runs whenever the loop ends without `break`. This includes a loop over nothing.

## A little deeper (optional)

`range` does not build a list in memory. It makes each number only when the loop asks for it. So `range(1_000_000)` uses almost no memory.

You can loop over a **dict** (lesson 11) too. `for key in d` gives the keys, and `d.items()` gives `(key, value)` pairs. A list has no `.items()`.

## Summary

- `while condition:` repeats while the condition is true. `for item in something:` goes through the items.
- `range(start, stop, step)` does not include `stop`.
- `break` leaves the loop. `continue` skips to the next round. Loop `else` runs when there was no `break`.
- `enumerate` gives the position and the item. `zip` walks several things together and stops at the shortest.
- A common pattern is the accumulator: start with a value (like `total = 0`) and update it in the loop.
