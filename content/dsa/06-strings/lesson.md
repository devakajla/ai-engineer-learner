---
title: "Strings"
summary: "Indexing, slicing and the string methods you need for text problems."
plan_ids: []
---

A string is a sequence of characters. Many problems are "do something to each character" or "check a property of the text".

## Indexing and slicing

```python
s = "python"
print(s[0])      # -> p
print(s[-1])     # -> n
print(s[1:4])    # -> yth
print(s[:2])     # -> py
print(s[2:])     # -> thon
print(s[::-1])   # -> nohtyp
```

`s[start:stop:step]`. `stop` is not included. A step of `-1` goes backwards.

> Strings are **immutable**. You cannot do `s[0] = "P"`. You build a new string.

## Methods that return a new string

```python
print("  hi  ".strip())            # -> hi
print("Hello".lower())             # -> hello
print("Hello".upper())             # -> HELLO
print("a-b-c".replace("-", "+"))   # -> a+b+c
```

## `split` and `join`

```python
words = "the quick fox".split()
print(words)               # -> ['the', 'quick', 'fox']
print("-".join(words))     # -> the-quick-fox
print("a,b,c".split(","))  # -> ['a', 'b', 'c']
```

`split()` with no argument splits on any whitespace and ignores extra spaces.

## Search and count

```python
s = "banana"
print(s.count("a"))      # -> 3
print(s.find("n"))       # -> 2
print(s.find("z"))       # -> -1   (not found)
print("nan" in s)        # -> True
print(s.startswith("ba"))   # -> True
```

## Checks on characters

```python
print("a".isalpha())    # -> True
print("5".isdigit())    # -> True
print(" ".isspace())    # -> True
print("A".isupper())    # -> True
print("a1".isalnum())   # -> True  (letters or digits only)
```

## Characters and numbers: `ord` and `chr`

```python
print(ord("a"))    # -> 97
print(chr(98))     # -> b
print(chr(ord("a") + 2))   # -> c
```

Letter positions: `ord(ch) - ord("a")` gives 0 for `a`, 1 for `b`, ...

## `sorted` on a string

`sorted(text)` returns a list of the characters in order. Two words with the same letters give equal lists.

```python
print(sorted("cab"))                     # -> ['a', 'b', 'c']
print(sorted("tea") == sorted("eat"))    # -> True
```

## Loop over a string

```python
count = 0
for ch in "hello world":
    if ch in "aeiou":
        count += 1
print(count)   # -> 3
```

## Common mistakes

- Trying to change a character in place.
- Forgetting that methods like `lower()` return a **new** string; the old one stays.
- Off-by-one in slices (`stop` is excluded).
- Mixing upper and lower case when comparing: normalise with `.lower()` first.

## Summary

- Index `s[i]`, slice `s[a:b:c]`, reverse with `s[::-1]`.
- `strip lower upper replace split join count find startswith`.
- `isalpha isdigit isalnum isspace`, and `sorted(text)`.
- `ord` and `chr` convert between letters and numbers.
- Strings are immutable: build a new one.
- Reference: `reference/strings.md`.
