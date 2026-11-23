---
title: "Loop drills"
summary: "Four loop patterns: accumulator, counter, flag and early exit, plus while loops with changing state."
plan_ids: []
---

Almost every beginner problem is one of a few loop patterns. Learn to recognise them.

## Pattern 1: accumulator

Keep a running value. Start it correctly, update it each round, return it at the end.

```python
def total(numbers):
    result = 0           # start: 0 for sums, 1 for products
    for n in numbers:
        result += n
    return result

print(total([4, 5, 6]))   # -> 15
```

## Pattern 2: counter

Count items that match a condition.

```python
def count_even(numbers):
    count = 0
    for n in numbers:
        if n % 2 == 0:
            count += 1
    return count

print(count_even([1, 2, 3, 4]))   # -> 2
```

## Pattern 3: flag / early exit

Return as soon as you know the answer. Do not keep looping.

```python
def has_negative(numbers):
    for n in numbers:
        if n < 0:
            return True      # found one, stop now
    return False             # checked everything

print(has_negative([3, -1, 5]))   # -> True
```

> Careful: `return False` goes **after** the loop, not inside it.

## Pattern 4: build a list

Start with an empty list and `append`.

```python
def squares(n):
    result = []
    for i in range(1, n + 1):
        result.append(i * i)
    return result

print(squares(4))   # -> [1, 4, 9, 16]
```

## `while` with changing state

Use `while` when you do not know how many rounds you need. Something must change each round.

```python
def steps_to_one(n):
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps

print(steps_to_one(6))   # -> 8
```

## `break` and `continue`

`break` leaves the loop. `continue` skips to the next round.

```python
for i in range(1, 6):
    if i == 3:
        continue
    if i == 5:
        break
    print(i)
# -> 1
# -> 2
# -> 4
```

## Common mistakes

- Starting a product at `0` instead of `1`.
- Putting `return` inside the loop when it should be after.
- Off-by-one: `range(n)` stops at `n - 1`. Use `range(1, n + 1)` to include `n`.
- A `while` loop where nothing changes the condition.

## Summary

- Accumulator: start value, update, return.
- Counter: `count += 1` when the condition is true.
- Early exit: `return` the moment you know; final `return` after the loop.
- Build a list: `[]` plus `append`.
- `while` for unknown number of rounds; make sure the state changes.
