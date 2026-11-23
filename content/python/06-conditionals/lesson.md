---
title: if / elif / else & match
summary: Make your code choose between options with if, elif and else, the one-line if, and match.
plan_ids: []
---

Programs need to make choices: show an error or a result, give a discount or not. Python does this with `if`. Since Python 3.10 it can also use `match`.

Remember from lesson 1: the lines **indented** under an `if` (4 spaces) belong to it.

## `if`, `elif`, `else`

```python
score = 72

if score >= 90:
    grade = "A"
elif score >= 70:
    grade = "B"
else:
    grade = "C"

print(grade)   # -> B
```

Read it like this:

- `if` checks the first condition.
- `elif` (short for "else if") checks the next one, only if the ones above were false.
- `else` runs when none of the conditions were true. It needs no condition.

Python checks from top to bottom and runs **only the first** one that is true. So **the order matters**: put the most specific condition first.

Here is a step-by-step example. A cinema gives a ticket price by age: under 5 is free, under 18 is 100, everyone else pays 200.

1. Check the smallest group first: `age < 5`.
2. Then the next: `age < 18`.
3. Finally `else` for everyone left.

```python
age = 12

if age < 5:
    price = 0
elif age < 18:
    price = 100
else:
    price = 200

print(price)   # -> 100
```

If you checked `age < 18` first, a 3 year old would pay 100, because that condition would already be true.

You can use any value as a condition, not only `True` and `False` (remember truthiness from lesson 5):

```python
items = []
if items:
    print("has items")
else:
    print("empty")   # -> empty
```

## Checking for `None`

Use `is None` to check for "no value". Do not use plain truthiness when `0` or `""` are real values:

```python
page_size = 0
if page_size is None:
    page_size = 20
print(page_size)   # -> 0   (0 is kept, because it is not None)
```

## Combining conditions

Use `and`, `or` and `not` (lesson 5) to join conditions:

```python
age, has_ticket = 20, True

if age >= 18 and has_ticket:
    print("enter")             # -> enter

if not (age >= 18 and has_ticket):
    print("stay out")
```

Chained comparisons read well too: `if 0 <= score <= 100:`.

To check if a value is one of several choices, use `in`:

```python
answer = "b"
if answer in ("a", "b"):
    print("valid")   # -> valid
```

## One-line choice (conditional expression)

For a simple "this or that" value, you can use one line:

```python
age = 20
label = "adult" if age >= 18 else "minor"
print(label)   # -> adult
```

The form is `value_if_true if condition else value_if_false`. Use it only for simple cases. For anything longer, use a normal `if`.

## Handle the bad cases first

Instead of putting an `if` inside an `if` inside an `if`, deal with the bad input first:

```python
age = -5

if age < 0:
    result = "invalid"
elif age < 18:
    result = "minor"
else:
    result = "adult"
print(result)   # -> invalid
```

Flat code is easier to read than deeply nested code.

## `match`

`match` compares one value against several **patterns** and runs the first pattern that fits. `_` matches anything, so it works as the default.

```python
status = 404

match status:
    case 200:
        text = "OK"
    case 404:
        text = "Not found"
    case 500 | 502 | 503:      # | means "or"
        text = "Server error"
    case _:
        text = "Other"

print(text)   # -> Not found
```

Only one `case` runs, and you do not need `break`.

You can add an extra condition to a case with `if`. This is called a **guard**. The name after `case` (here `x`) takes the value, so the guard can use it:

```python
n = 15
match n:
    case x if x < 0:
        print("negative")
    case 0:
        print("zero")
    case _:
        print("positive")   # -> positive
```

> For simple choices, an `if` / `elif` chain is just as good. Use `match` when it makes the code clearer.

## A little deeper (optional)

`match` can also take apart lists and pick out the pieces:

```python
command = ["go", "north"]

match command:
    case ["quit"]:
        print("bye")
    case ["go", direction]:
        print("going", direction)   # -> going north
    case _:
        print("unknown")
```

A bare name in a `case` (like `direction` above) **captures** the value and always matches. So `case color:` does **not** compare with a variable called `color`. It takes whatever value comes in. To compare, use a literal value like `200`.

## Common mistakes

- Using `=` instead of `==` in a condition. `if x = 5` is a `SyntaxError`.
- Putting the checks in the wrong order. If `score >= 70` comes before `score >= 90`, then 95 becomes a "B".
- Writing `if x == "a" or "b":`. This is always true. Write `x in ("a", "b")`.
- Wrong or mixed indentation. This gives `IndentationError`.
- Writing `case name:` in a `match` and expecting a comparison. A bare name captures the value.

## Summary

- `if` / `elif` / `else`: the first true branch runs, and indentation marks the block.
- Put the most specific condition first.
- Use `is None` to check for no value.
- `a if cond else b` is a one-line choice. Keep it simple.
- Handle bad cases first to keep code flat.
- `match` / `case` chooses by pattern. `_` is the default, `|` means or, and `case x if ...` adds a guard.
