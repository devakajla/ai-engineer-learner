# 2. Variables, numbers and strings

Everything a program does is **working with data**: a price, a name, an age. This chapter covers how Python holds data (variables), and the two kinds you will use most: numbers and text.

## Variables: labels on boxes

In daily life you label a box "kitchen" so you know what is inside. A **variable** is a label for a value that Python keeps in memory.

```python
age = 25
```

Read this as: "make the value `25`, and stick the label `age` on it." The `=` sign here does **not** mean "equal". It means "store this under that name". Left side is the label, right side is the value.

You can move the label to a new value at any time:

```python
age = 25
age = 26
print(age)
# -> 26
```

The old value `25` is no longer reachable through `age`, so Python throws it away. The label simply points somewhere else now.

@@ flow | Figure 2.1: a variable is a label that points to a value.
age|the label|blue -points to-> 26|the value in memory|green
@@ end

**Naming rules.** Letters, digits and `_`, and it cannot start with a digit. By habit we use `lower_case_with_underscores`, like `total_price`. Choose names that say what the value is. `price` is better than `p`.

## Types: what kind of data is it?

Every value has a **type**, which says what kind of thing it is and what you may do with it. You can add two numbers, but adding a number to a word makes no sense.

| Type | Meaning | Example |
| --- | --- | --- |
| `int` | whole number | `42` |
| `float` | number with a decimal point | `3.14` |
| `str` | text ("string") | `"hello"` |
| `bool` | true or false | `True`, `False` |
| `NoneType` | "nothing here" | `None` |

Ask Python with `type`:

```python
print(type(5), type(5.0), type("5"), type(True), type(None))
# -> <class 'int'> <class 'float'> <class 'str'> <class 'bool'> <class 'NoneType'>
```

Notice that `5`, `5.0` and `"5"` look similar but are three different types. The quote marks make `"5"` text. You cannot do maths on it.

Python works out the type itself from the value. You do not declare it. This is called **dynamic typing**. (Later you will add optional *type hints* to document what you expect.)

## Numbers and arithmetic

```python
a = 7
b = 2
print(a + b, a - b, a * b)
# -> 9 5 14
print(a / b)
# -> 3.5
print(a // b)
# -> 3
print(a % b)
# -> 1
print(a ** b)
# -> 49
```

Three of these need explaining, because they are the ones that confuse people:

- `/` is normal division and **always gives a float**, even for `8 / 2` (that is `4.0`).
- `//` is **floor division**: divide, then throw away the part after the decimal point. Think "how many full times does 2 fit in 7?" Answer: 3.
- `%` is the **remainder**: what is left over. 7 = 3 groups of 2, with 1 left. Checking `n % 2 == 0` is the classic test for an even number.
- `**` is "to the power of".

Order of operations is the same as in school maths: brackets first, then `**`, then `*` and `/`, then `+` and `-`. When unsure, add brackets. They cost nothing and make the meaning clear.

### The float surprise

```python
print(0.1 + 0.2)
# -> 0.30000000000000004
```

This is not a Python bug. Computers store decimals in binary, and the number 0.1 cannot be stored exactly in binary, just as 1/3 cannot be written exactly in decimal (0.3333...). The tiny error shows up.

What to do: never compare floats with `==`. Round for display: `round(0.1 + 0.2, 2)` gives `0.3`. For money, use whole numbers (cents) or the `decimal` module.

## Strings: text

A string is a sequence of characters between quotes. Single `'` and double `"` quotes are the same. Use one style and stay with it.

### Joining and formatting

You can join with `+`, but there is a much nicer way called an **f-string**. Put an `f` before the quote, and write variables inside `{ }`:

```python
name = "Asha"
age = 26
print(f"Hi {name}, next year you are {age + 1}")
# -> Hi Asha, next year you are 27
```

Inside the braces you can write any expression, not only a name. The result is turned into text and placed there. You will use f-strings every day.

Format details go after a colon:

```python
print(f"{3.14159:.2f} {1234567:,} {5:03d}")
# -> 3.14 1,234,567 005
```

`.2f` means "2 digits after the point", `,` adds thousands separators and `03d` pads with zeros to width 3.

### Indexing and slicing

Each character has a position number, starting at **0**, not 1. Negative numbers count from the end.

@@ grid 3 | Figure 2.2: positions in the word "python".
p|index 0, or -6|blue
y|index 1, or -5|blue
t|index 2, or -4|blue
h|index 3, or -3|blue
o|index 4, or -2|blue
n|index 5, or -1|blue
@@ end

```python
w = "python"
print(w[0], w[-1])
# -> p n
print(w[1:4])
# -> yth
print(w[:2], w[::-1])
# -> py nohtyp
```

A **slice** `w[start:stop]` takes characters from `start` up to, but **not including**, `stop`. That is why `w[1:4]` gives positions 1, 2, 3. Leave out a side to mean "from the beginning" or "to the end". The step `-1` walks backwards, which reverses the string.

### Strings cannot be changed

```python
w = "python"
w[0] = "P"
# -> TypeError: 'str' object does not support item assignment
```

A string is **immutable**, a fancy word that means "cannot be changed after it is made". To get a changed text, you build a **new** string, for example `"P" + w[1:]`. Remember this word. It returns in chapter 8 and is a favourite interview topic.

### Useful string methods

A **method** is an action that belongs to a value. You write it with a dot: `value.method()`. Methods on strings never change the original. They return a new string.

```python
s = "  Hello, World  "
print(s.strip())
# -> Hello, World
print(s.strip().lower())
# -> hello, world
print(s.strip().replace("World", "Python"))
# -> Hello, Python
print("a,b,c".split(","))
# -> ['a', 'b', 'c']
print("-".join(["a", "b", "c"]))
# -> a-b-c
```

`strip` removes spaces at both ends. `split` cuts a string into a list at every comma. `join` is its opposite: glue the pieces together using the text before the dot as the glue. (Lists come in chapter 4.)

Because methods return new values, you can **chain** them, as in `s.strip().lower()`: each step works on the result of the previous one.

## Converting between types

```python
print(int("42") + 1)
# -> 43
print("42" + "1")
# -> 421
print(str(42) + "1")
# -> 421
```

`int("42")` turns text into a number, so you can add. Without it, `+` between two strings just **joins** them. Use `int()`, `float()`, `str()` and `bool()` to convert. If the text is not a number (`int("abc")`), Python raises a `ValueError`.

Anything typed by a user comes in as text, so you convert it almost every time: `age = int(input("Age? "))`.

## Truthy and falsy

Any value can be treated as true or false. The rule is simple: **empty or zero means False, everything else means True.**

```python
print(bool(0), bool(""), bool([]), bool(None))
# -> False False False False
print(bool("0"), bool(-1), bool("False"))
# -> True True True
```

Note the last line: the text `"0"` and the text `"False"` are **not empty**, so they count as true. A surprise to many beginners.

One more twist: `bool` is a kind of `int`. `True` behaves like 1 and `False` like 0:

```python
print(True + True, isinstance(True, int))
# -> 2 True
```

## Worked example: a small bill

Goal: the user buys 3 items at 249.99 each. Show the total with 18% tax, rounded to 2 decimals. Plan first, then code.

1. Store the inputs in variables.
2. Calculate the subtotal.
3. Calculate the tax.
4. Print everything in a readable way.

```python
price = 249.99
count = 3
subtotal = price * count
tax = subtotal * 0.18
total = subtotal + tax
print(f"Subtotal: {subtotal:.2f}")
print(f"Tax:      {tax:.2f}")
print(f"Total:    {total:.2f}")
# -> Subtotal: 749.97
# -> Tax:      134.99
# -> Total:    884.96
```

Notice the **pattern**: inputs, then calculations stored in named variables, then output. Each step has its own name, which makes the code readable and easy to fix. This is how you should approach the first exercise.

::: {.box .checkpoint}
**Checkpoint:** you can predict, before running, what `7 // 2`, `7 % 2`, `"7" + "2"` and `int("7") + 2` print.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Treating `=` as "equals". It stores a value. Comparing uses `==` (chapter 3).
- Adding a number to text: `"Age: " + 26` is a `TypeError`. Use an f-string.
- Comparing floats with `==`.
- Thinking slices include the end position.
- Expecting `s.upper()` to change `s`. It returns a new string. Write `s = s.upper()` to keep it.
- Starting to count from 1 instead of 0.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. A shirt costs 799 and has a 15% discount. Print the final price with 2 decimals.
2. Given `minutes = 135`, print it as hours and minutes ("2 h 15 min") using `//` and `%`.
3. Given `text = "  Python Is Fun  "`, print it trimmed, in lower case, with `Fun` replaced by `Great`.
4. Print the first and last character of any word and the word reversed.
5. Predict the result, then check: `bool("0")`, `bool(0.0)`, `True + 1`, `10 / 5`, `type(10 // 5)`.
6. **Think:** why is `0.1 + 0.2 == 0.3` false, and what would you do when comparing prices?
:::
