---
title: Strings & f-strings
summary: "Text in Python: how to pick letters out of it, change it with methods, and format it with f-strings."
plan_ids: []
---

A **string** (`str`) is text. Names, emails, messages and web responses are all strings, so you will use them all the time. In this lesson you will learn to pick parts of a string, use the common string tools, and build nice-looking text.

## Creating strings

Put text inside single or double quotes. They work the same, so pick one style and stick to it.

```python
a = 'single'
b = "double"
c = """first line
second line"""          # triple quotes can span many lines
print(c)
# -> first line
# -> second line
```

A backslash `\` starts a special character (an **escape sequence**): `\n` is a new line, `\t` is a tab.

```python
print("a\tb\nc")
# -> a	b
# -> c
path = r"C:\new\table"   # r"..." (raw string): backslashes are just backslashes
```

## Indexing and slicing

Every character has a position called an **index**. The first character is at index `0`. A negative index counts from the end.

```python
s = "python"
s[0]     # -> 'p'
s[1]     # -> 'y'
s[-1]    # -> 'n'      last character
len(s)   # -> 6        number of characters
s[10]    # IndexError: string index out of range
```

A **slice** takes a part of the string: `s[start:stop]`. It starts at `start` and stops **before** `stop`.

```python
s = "python"
s[0:2]    # -> 'py'      indexes 0 and 1
s[2:]     # -> 'thon'    from index 2 to the end
s[:2]     # -> 'py'      from the start up to index 2
s[-3:]    # -> 'hon'     the last 3 characters
```

You can add a third number, the **step**: `s[start:stop:step]`. A step of `-1` goes backwards, so it reverses the string.

```python
s[::2]     # -> 'pto'     every 2nd character
s[::-1]    # -> 'nohtyp'  reversed
s[2:100]   # -> 'thon'    a slice never raises IndexError
```

## Strings cannot be changed

A string is **immutable**: you cannot change a letter inside it.

```python
s = "cat"
s[0] = "b"         # TypeError: 'str' object does not support item assignment
s = "b" + s[1:]    # make a new string instead
print(s)           # -> bat
```

Every string method gives you a **new** string. The old one stays the same:

```python
name = "  Dev  "
name.strip()          # -> 'Dev'
print(name)           # -> '  Dev  '   not changed!
name = name.strip()   # save the result to keep it
print(name)           # -> Dev
```

## Methods you will use every day

A **method** is a function that belongs to a value. You call it with a dot: `"hi".upper()`.

| Method | Example | Result |
|---|---|---|
| `lower()` / `upper()` / `title()` | `"Hi".lower()` | `'hi'` |
| `strip()` | `" x ".strip()` | `'x'` (removes spaces at both ends) |
| `split(sep)` | `"a,b,c".split(",")` | `['a', 'b', 'c']` |
| `split()` (no argument) | `" a  b ".split()` | `['a', 'b']` (splits on any spaces) |
| `sep.join(items)` | `"-".join(["a", "b"])` | `'a-b'` |
| `replace(old, new)` | `"aaa".replace("a", "b", 2)` | `'bba'` |
| `find(sub)` | `"hello".find("l")` | `2` (gives `-1` if not found) |
| `startswith` / `endswith` | `"file.py".endswith(".py")` | `True` |
| `count(sub)` | `"banana".count("a")` | `3` |
| `isdigit()` / `isalpha()` | `"42".isdigit()` | `True` |
| `partition(sep)` | `"k=v=w".partition("=")` | `('k', '=', 'v=w')` |

The square brackets `[...]` in the results are **lists**. You will learn lists in lesson 8. `partition` gives a three-part **tuple** (lesson 9): the part before, the separator, and the part after.

To check if some text is inside another text, use `in`:

```python
"py" in "python"    # -> True
"py" in "happy"     # -> True
"z" in "python"     # -> False
```

You can also repeat a string with `*`:

```python
"ab" * 3     # -> 'ababab'
```

Here is a step-by-step example. Do two strings match, ignoring capital letters and spaces?

1. Remove the spaces with `replace(" ", "")`.
2. Make everything small with `lower()`.
3. Do this to both strings, then compare with `==`.

```python
a = "Dev Ops"
b = "devops"
a.replace(" ", "").lower() == b.replace(" ", "").lower()   # -> True
```

## f-strings: text with values inside

Put an `f` before the opening quote. Anything inside `{ }` is worked out and put into the text.

```python
name = "Dev"
score = 0.8567
f"{name} scored {score}"                       # -> 'Dev scored 0.8567'
f"{name.upper()} has {len(name)} letters"      # -> 'DEV has 3 letters'
```

After a `:` inside the braces you can set the **format**:

```python
f"{score:.2f}"       # -> '0.86'        2 digits after the point
f"{score:.1%}"       # -> '85.7%'       as a percentage
f"{1234567:,}"       # -> '1,234,567'   commas between thousands
f"{1234.5:,.2f}"     # -> '1,234.50'    commas and 2 decimals
f"[{name:>6}]"       # -> '[   Dev]'    right-align in 6 characters
f"[{name:<6}]"       # -> '[Dev   ]'    left-align in 6 characters
f"[{name:^7}]"       # -> '[  Dev  ]'   centre in 7 characters
f"{7:03d}"           # -> '007'         fill with zeros to width 3
```

The pattern is `{value:[align][width][,][.decimals][type]}`. You do not need to remember it all. Look it up when you need it.

## Common mistakes

- Calling `s.strip()` and forgetting to save the result. The string does not change by itself.
- Using `find` and not checking for `-1`.
- Writing `"5" + 5`. This is a `TypeError`. Use `str(5)` or an f-string.
- Writing `split(" ")` when you mean `split()`. With one space `" "`, repeated spaces give empty strings.

## A little deeper (optional)

**Why `"".join(parts)` is better than `s += part` in a long loop.** Strings cannot change, so `s += part` makes a whole new copy of the string every time. With thousands of pieces, this gets very slow. `join` builds the final string once. Collect the pieces in a list and join them at the end. You will use this after the Loops lesson.

**`"a,b,,c".split(",")`** gives `['a', 'b', '', 'c']`. The empty string between the two commas is kept.

**Unicode.** Python strings hold any language. `len("नमस्ते")` is `6`, the number of characters (code points). Turning a string into bytes is **encoding**, and going back is **decoding**:

```python
"é".encode("utf-8")           # -> b'\xc3\xa9'   2 bytes
b"\xc3\xa9".decode("utf-8")   # -> 'é'
```

**Debug form.** `f"{score=}"` gives `'score=0.8567'`. It is handy for quick checks.

## Summary

- A string is text. It cannot be changed, and its methods return new strings.
- Index from `0`. Negative indexes count from the end. Slices `[start:stop:step]` stop before `stop` and never fail.
- `split`, `join`, `strip`, `replace`, `lower`, `startswith` and `in` handle most text work.
- f-strings put values into text, and `:.2f`, `:,`, `:<10`, `:>10` and `:03d` control how they look.
