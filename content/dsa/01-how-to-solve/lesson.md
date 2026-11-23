---
title: "How to solve a problem"
summary: "A 5-step routine for every coding problem, and the basics of writing and testing a function."
plan_ids: []
---

This track is a gym. You will not learn new theory here; you will write a lot of small programs until Python feels natural. Real DSA comes after.

You already know the syntax from the Python track (variables, `if`, loops, functions). Here you practise using it. If something feels shaky, open the matching Python lesson or the `reference/` folder.

## The 5-step routine

Use this for **every** problem, even easy ones. It becomes a habit, and the habit is the real skill.

1. **Understand.** Say the problem in your own words. What goes in? What comes out?
2. **Try an example by hand.** Take the example and solve it on paper, step by step.
3. **Plan in plain words.** Write 2-4 lines like "loop over the numbers, add each to a total, return the total".
4. **Code.** Turn the plan into Python. Keep it simple first.
5. **Test the edges.** Try empty input, one item, zero, negative numbers, repeated values.

> Most beginners jump to step 4. Steps 2 and 3 are where problems actually get solved.

## A function takes input and returns output

```python
def add(a, b):
    return a + b

print(add(2, 3))   # -> 5
```

Every exercise in this track asks for a function. The tests call it with inputs and compare what it **returns**.

## `return` vs `print`

`print` shows text on screen. `return` hands a value back to the caller. The tests only see the returned value.

```python
def bad(a, b):
    print(a + b)       # shows 5, returns None

def good(a, b):
    return a + b       # gives 5 back

x = good(2, 3)
print(x)   # -> 5
y = bad(2, 3)   # prints 5
print(y)   # -> None
```

> Common trap: your function prints the right answer but the test fails. You forgot `return`.

## Testing your own function

Before you run the real tests, try a few calls yourself:

```python
def is_even(n):
    return n % 2 == 0

print(is_even(4))    # -> True
print(is_even(7))    # -> False
print(is_even(0))    # -> True
```

Pick small inputs where you already know the answer. If one is wrong, you found a bug early.

## Conditions that return a value

You can return from inside an `if`. The function stops at the first `return` it reaches.

```python
def sign(n):
    if n > 0:
        return "positive"
    if n < 0:
        return "negative"
    return "zero"

print(sign(5))    # -> positive
print(sign(0))    # -> zero
```

## How each exercise is laid out

- The **signature** is given. Do not change the name.
- **Think first** is a question to ask yourself before you code.
- **Hint** names a tool you may need. Use it only if you are stuck.
- Run the tests. Read the failure message: it tells you which input broke.

## Common mistakes

- Using `print` instead of `return`.
- Writing code before understanding one example by hand.
- Testing only the example from the prompt and skipping edge cases.
- Changing the function name or parameter order.

## Summary

- Use the 5 steps: understand, example by hand, plan, code, test edges.
- Functions take input and **return** output; tests read the return value.
- A function stops at the first `return` it reaches.
- Test with small inputs where you know the answer.
