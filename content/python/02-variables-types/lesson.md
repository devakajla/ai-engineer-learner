---
title: Variables & data types
summary: A variable is a name for a value, and every value has a type. Learn to name values, check their type and know which ones can change.
plan_ids: []
---

A **variable** is a name you give to a value, so you can use that value again later. Think of a sticky note with a name written on it. You stick the note on a value. Now you can find the value by its name.

Almost every program uses variables, so this lesson is worth getting right.

## Your first variable

```python
age = 25
name = "Dev"
print(age)    # -> 25
print(name)   # -> Dev
```

The `=` sign means "give this name to this value". It does **not** mean "is equal to" like in maths.

You can move a name to a new value at any time:

```python
age = 25
age = 26
print(age)    # -> 26
```

A few handy shortcuts:

```python
count = 0
count += 1          # same as: count = count + 1
print(count)        # -> 1

x = y = 0           # both names get the value 0

a, b = 1, 2         # two names in one line
a, b = b, a         # swap the two values
print(a, b)         # -> 2 1
```

## Naming rules

- Use letters, digits and `_`. A name cannot start with a digit.
- Names are case-sensitive: `age` and `Age` are two different names.
- Write names in `snake_case` (small letters with `_` between words), like `user_name`.
- Write constants (values that never change) in `UPPER_CASE`, like `MAX_SIZE`.
- Do not use a name that Python already uses, like `list`, `str`, `type` or `id`. These are **built-in** names. If you write `list = [1, 2]`, you cannot use the real `list` later.

## What is a type?

Every value has a **type**. The type tells Python what kind of value it is and what you can do with it. You can add two numbers, but you cannot add a number to a word.

| Type | What it is | Example |
|---|---|---|
| `int` | whole number | `42`, `-7` |
| `float` | number with a decimal point | `3.14` |
| `str` | text (a "string") | `"hello"` |
| `bool` | yes or no | `True`, `False` |
| `NoneType` | "no value" | `None` |

You will meet more types later: `list`, `tuple`, `dict` and `set` in lessons 8 to 11.

Use `type()` to see the type of a value:

```python
type(5)        # -> <class 'int'>
type(2.5)      # -> <class 'float'>
type("hi")     # -> <class 'str'>
type(True)     # -> <class 'bool'>
type(None)     # -> <class 'NoneType'>
```

If you want only the short name of the type, add `.__name__`:

```python
type(5).__name__       # -> 'int'
type("hi").__name__    # -> 'str'
```

You do not declare a type in Python. Python looks at the value. The same name can point to a different type later:

```python
x = 10        # x points to an int
x = "ten"     # now x points to a str. This is allowed.
print(type(x))   # -> <class 'str'>
```

## Check a type with `isinstance()`

`isinstance(value, type)` answers "is this value of this type?" with `True` or `False`.

```python
isinstance(5, int)               # -> True
isinstance("5", int)             # -> False
isinstance(5, (int, float))      # -> True   (a tuple of types means "any of these")
```

Real programs prefer `isinstance` over `type()`, because it also works for **subclasses**. A subclass is a more specific kind of a type. You will learn about classes in Level 2.

There is one surprise. Python treats `True` as the number 1 and `False` as the number 0. So a `bool` counts as an `int`:

```python
isinstance(True, int)    # -> True
True + True              # -> 2
isinstance(True, bool)   # -> True
isinstance(5, bool)      # -> False
```

> Remember this surprise. If you want to treat a `bool` differently from an `int`, you must ask about `bool` too. You can join checks with `and` and `not` (you will learn them in lesson 5).

## `None`: no value

`None` means "there is no value here yet". It is the only value of type `NoneType`.

```python
result = None
if result is None:
    print("nothing yet")    # -> nothing yet
```

To check for `None`, write `is None`, not `== None`. The "A little deeper" section below explains why.

## Values that can change and values that cannot

Some values can be changed after you make them. They are **mutable**. Other values can never change. They are **immutable**.

| Mutable (can change) | Immutable (cannot change) |
|---|---|
| `list`, `dict`, `set` | `int`, `float`, `bool`, `str`, `tuple`, `None` |

A string is immutable. When you "change" a string, Python makes a **new** string and moves your name to it. The old string is not touched:

```python
s = "hi"
t = s              # t is another name for the same "hi"
s = s + "!"        # + joins strings (more in lesson 4). This makes a NEW string
print(s)           # -> hi!
print(t)           # -> hi   (the old string did not change)
```

## Two names, one value

This is the most useful idea in this lesson. A name is like a sticky note. When you write `b = a`, you do **not** copy the value. You stick a second note on the **same** value.

For immutable values (numbers, strings) this is safe, because the value can never change. For mutable values it matters. Here `[1, 2, 3]` is a **list**, a group of values in square brackets (you will learn lists in lesson 8). `.append(4)` adds a value at the end of the list.

```python
a = [1, 2, 3]
b = a              # a second name for the SAME list
b.append(4)        # change the list through the name b
print(a)           # -> [1, 2, 3, 4]   a sees the change too
print(b)           # -> [1, 2, 3, 4]
```

There is only one list, with two names on it. `b = a` copied nothing.

## A little deeper (optional)

You can skip this section on your first read. It explains the ideas behind the sticky notes.

**Every value has three things:**

| Property | How to see it | Can it change? |
|---|---|---|
| Identity | `id(value)`, a number that is unique while the value exists | never |
| Type | `type(value)` | never |
| Content | the data itself | only if the type is mutable |

**`==` and `is` ask different questions.** `==` asks "do these have the same content?". `is` asks "are these the very same value (same identity)?".

```python
a = [1, 2]
b = [1, 2]
print(a == b)    # -> True    same content
print(a is b)    # -> False   two separate lists
```

**Why `is None`?** There is exactly one `None` in the whole program. So the right question is "is this *the* `None`?", and `is` asks that. `== None` can give a wrong answer, because some types change how `==` works.

**Why is `bool` an `int`?** `bool` is a subclass of `int`. That is why `True == 1` and `False == 0`.

## Common mistakes

- Thinking `b = a` makes a copy of a list. It does not. Both names share one list.
- Writing `== None` instead of `is None`.
- Forgetting that `True` counts as the number 1, so `isinstance(True, int)` is `True`.
- Using a built-in name like `list`, `dict`, `str`, `id` or `type` as your own variable name.

## Summary

- A variable is a **name** for a value. `=` gives the name to the value, and it never makes a copy.
- Every value has a type. See it with `type()`. Check it with `isinstance()`.
- A `bool` counts as an `int`, so `isinstance(True, int)` is `True`.
- Check for nothing with `x is None`.
- Mutable values (`list`, `dict`, `set`) can change in place. Immutable values (`int`, `float`, `bool`, `str`, `tuple`, `None`) cannot.
- `==` compares content. `is` asks if it is the same value.
