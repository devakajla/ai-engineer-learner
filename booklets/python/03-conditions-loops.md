# 3. Conditions and loops

So far, your program runs top to bottom and does the same thing every time. Real programs **decide** ("is the user an adult?") and **repeat** ("do this for every item"). These two powers, **conditions** and **loops**, are the heart of programming.

## Booleans and comparisons

A condition is a question with a yes/no answer. Python writes the answer as a `bool`: `True` or `False`. You get one by **comparing** two values.

| Operator | Question it asks |
| --- | --- |
| `==` | are they equal? |
| `!=` | are they different? |
| `<`, `>`, `<=`, `>=` | smaller, bigger, and so on |
| `in` | is it inside? |

```python
print(5 == 5, 5 != 5, 3 < 5 < 10, "a" in "cat")
# -> True False True True
```

Two things to notice. First, `==` (two signs) **asks** a question, while `=` (one sign) **stores** a value. Mixing them up is the most common beginner error. Second, Python lets you chain comparisons the way maths does: `3 < 5 < 10` means "5 is between 3 and 10".

### Combining questions: `and`, `or`, `not`

```python
print(not True)
# -> False
```

`and` is true only if **both** sides are true. `or` is true if **at least one** is. `not` flips the answer. Use brackets when mixing them, so a reader does not need to remember the priority rules.

### The surprising part: what `and` / `or` really return

They do not always return `True` or `False`. They return **one of the two values themselves**.

```python
print(0 or "default")
# -> default
print("" or "x")
# -> x
print(5 and 6)
# -> 6
```

The rule: `a or b` gives `a` if `a` is truthy (chapter 2), otherwise `b`. `a and b` gives `a` if `a` is falsy, otherwise `b`. Python stops as soon as the answer is known (**short-circuit**). A common use is a fallback value: `name = user_input or "guest"`.

### `==` versus `is`

`==` asks "do they have the same **value**?". `is` asks "are they the very **same object** in memory?". Think of two printed copies of one book (equal content, different objects) versus one single book.

```python
print([] == [], [] is [])
# -> True False
x = None
print(x is None)
# -> True
```

Use `is` almost only for `None` (and `True`/`False`). For everything else, use `==`.

## `if`, `elif`, `else`

An `if` runs a block of lines only when its condition is true. The block is the indented lines after the colon.

```python
age = 20
if age >= 18:
    print("adult")
elif age >= 13:
    print("teen")
else:
    print("child")
# -> adult
```

How to read it: Python checks the conditions **from top to bottom** and runs the **first** one that is true, then skips the rest. `else` is the fallback when nothing matched. Because the order matters, put the most specific check first.

The colon `:` at the end of the line and the 4-space indentation are required. They are how Python knows where the block begins and ends.

## Loops: repeating work

### `for`: once for each item

```python
for i in range(3):
    print(i, end=" ")
# -> 0 1 2
```

Read it as: "for each value `i` in this sequence, do the indented block." `range(3)` produces 0, 1, 2 (it stops *before* 3, just like slices). `range(2, 10, 3)` means start at 2, stop before 10, step by 3, giving 2, 5, 8.

You can loop over any sequence, such as the letters of a string or items of a list (chapter 4). The most useful loop shape is the **accumulator**: keep a running result in a variable.

```python
total = 0
for n in [1, 2, 3, 4]:
    total += n
print(total)
# -> 10
```

`total += n` is shorthand for `total = total + n`. Step by step: total is 0, then 1, then 3, then 6, then 10. Start the accumulator **before** the loop, update it **inside**, and use it **after**. You will use this pattern hundreds of times.

### `while`: repeat as long as something is true

```python
count = 0
while count < 3:
    count += 1
print(count)
# -> 3
```

Use `for` when you know what to loop over. Use `while` when you only know the **stopping condition**. A `while` must change something that eventually makes the condition false, otherwise it runs forever (an **infinite loop**). If that happens, press `Ctrl+C`.

### `break`, `continue` and `else`

```python
for i in range(10):
    if i == 3:
        break
    if i % 2 == 0:
        continue
    print("odd", i)
# -> odd 1
```

`break` leaves the loop completely. `continue` skips the rest of this round and jumps to the next one. Here: 0 is even (skipped), 1 prints, 2 is skipped, 3 breaks the loop.

A loop can have an `else` that runs only if the loop finished **without** a `break`. It is rarely needed, but it appears in interviews.

### Two helpers you will love: `enumerate` and `zip`

```python
for i, ch in enumerate("ab"):
    print(i, ch)
# -> 0 a
# -> 1 b
for a, b in zip([1, 2], ["x", "y"]):
    print(a, b)
# -> 1 x
# -> 2 y
```

`enumerate` gives you the **position and the item** together, so you do not need a counter variable. `zip` walks **two sequences side by side**. Both give you two values per round, and `for i, ch in ...` unpacks them into two names.

## Worked example: count the vowels

Problem: given a word, count its vowels. Think before typing. This is the same **accumulator** pattern, with a condition inside.

1. Need a counter that starts at 0.
2. Look at each letter.
3. If the letter is a vowel, add 1.
4. After the loop, the counter is the answer.

```python
word = "education"
count = 0
for letter in word:
    if letter in "aeiou":
        count += 1
print(count)
# -> 5
```

Test by hand: e, u, a, i, o are vowels, so 5. Always check one example by hand, and also think of **edge cases**: an empty word gives 0, and capital letters (`"A"`) would be missed. Fixing that is a good exercise: lower-case the word first.

::: {.box .checkpoint}
**Checkpoint:** you can explain the difference between `=` and `==`, between `==` and `is`, and what `break` and `continue` do. You can write an accumulator loop without looking.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Writing `if x = 5` instead of `if x == 5`.
- Forgetting the colon, or wrong indentation.
- Using `is` to compare numbers or text.
- A `while` loop that never changes its condition.
- Setting the accumulator **inside** the loop, so it resets each round.
- Off-by-one with `range`: `range(5)` is 0 to 4, not 1 to 5.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Given a score, print the grade: 90+ is "A", 75+ is "B", 50+ is "C", otherwise "F".
2. Sum all numbers from 1 to 100 with a loop. Check against the formula `100 * 101 // 2`.
3. Print all multiples of 7 below 100 using `range` with a step.
4. Count how many words in `"the cat and the hat".split()` equal `"the"`.
5. Find the first number divisible by both 3 and 5 that is greater than 100, using `while`.
6. Use `enumerate` to print `1. apple`, `2. pear` for a list of fruits (counting from 1: `enumerate(items, start=1)`).
7. **Think:** why is `x or "guest"` a reasonable default, and what bug can it cause when `x` is `0`?
:::
