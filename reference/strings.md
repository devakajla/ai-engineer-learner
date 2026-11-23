# Strings

Strings are **immutable** sequences of characters. Every "change" returns a new string.

| Method | Does |
| --- | --- |
| `s[i]`, `s[a:b:c]` | index, slice |
| `s.lower()` `s.upper()` | change case |
| `s.strip()` | remove spaces at both ends |
| `s.split(sep)` | break into a list |
| `sep.join(list)` | join a list into a string |
| `s.replace(old, new)` | replace all |
| `s.find(x)` | index or `-1` |
| `s.count(x)` | non-overlapping count |
| `s.startswith(x)` `s.endswith(x)` | prefix / suffix test |
| `s.isalpha()` `isdigit()` `isalnum()` `isspace()` | character-type test |
| `ord(ch)` `chr(n)` | letter <-> number |

## Index and slice
```python
s = "python"
print(s[0], s[-1], s[1:4], s[::-1])   # -> p n yth nohtyp
```
**Gotcha:** `stop` is excluded. `s[0] = "P"` is an error. Lesson: `dsa/06-strings`.

## `split` and `join`
```python
print("a b  c".split())          # -> ['a', 'b', 'c']
print("a,b".split(","))         # -> ['a', 'b']
print("-".join(["x", "y"]))      # -> x-y
```
**Theory:** `split()` with no argument splits on any whitespace and drops empty parts. `join` is called on the **separator**.

## `strip`, `lower`, `upper`, `replace`
```python
print("  hi ".strip(), "Hi".lower(), "Hi".upper())   # -> hi hi HI
print("a-b".replace("-", "+"))   # -> a+b
```
**Gotcha:** they return a new string. `s.upper()` alone changes nothing.

## `find`, `count`, `in`, `startswith`
```python
s = "banana"
print(s.find("n"), s.find("z"), s.count("a"))   # -> 2 -1 3
print("nan" in s, s.startswith("ba"))           # -> True True
```
**Gotcha:** `find` returns `-1` when missing, and `0` is a valid index. Do not write `if s.find(x):`.

## Character checks
```python
print("a".isalpha(), "5".isdigit(), "a1".isalnum(), " ".isspace())   # -> True True True True
```

## `ord` and `chr`
```python
print(ord("a"), chr(98))                # -> 97 b
print(chr((ord("y") - ord("a") + 3) % 26 + ord("a")))   # -> b
```
**Theory:** letter position = `ord(ch) - ord("a")`. Use `% 26` to wrap around.

## `sorted(text)`
```python
print(sorted("cab"))   # -> ['a', 'b', 'c']
```
Sorted letters make a good key for anagrams: `"".join(sorted(word))`.

## Building strings
Use `+=` in loops for small strings, or build a list and `"".join(parts)`.
