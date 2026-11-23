---
title: "Stack and monotonic stack"
summary: "Use a stack when the newest item decides what happens next, and a monotonic stack to find the next bigger or smaller value."
plan_ids: []
---

A **stack** is "last in, first out". In Python a plain `list` is a stack: `append` pushes, `pop()` removes the top, `stack[-1]` looks at the top. All three are O(1).

Use a stack when **the most recent unfinished thing** is the one you must deal with first: brackets, undo, nested structures, and "the nearest bigger value".

> Watch the intro video first. Each exercise from 01 to 06 has a video segment where the same problem is solved.

## When to think "stack"

1. Matching pairs or nesting: brackets, tags, `k[text]`.
2. "Undo" or "cancel the previous": backspace, remove duplicates.
3. "Next greater / smaller element", "how many days until...".
4. You keep a list of things that are **waiting** for something to come.

## Type 1: plain stack (match, undo)

```python
def is_valid(s):
    pair = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pair:                       # a closer
            if not stack or stack.pop() != pair[ch]:
                return False
        else:                                # an opener
            stack.append(ch)
    return not stack                         # nothing left open

print(is_valid("{[()]}"))   # -> True
print(is_valid("(]"))       # -> False
```

The most recent opener must be closed first. That is exactly what a stack gives you.

## Type 2: monotonic stack (next greater element)

Keep a stack of **indexes** of items that are still waiting for their "next greater". When a bigger value arrives, it answers every smaller waiting item on top of the stack.

```python
def next_greater(nums):
    result = [-1] * len(nums)
    stack = []                               # indexes, values decreasing
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            result[stack.pop()] = x
        stack.append(i)
    return result

print(next_greater([1, 3, 2, 4]))   # -> [3, 4, 4, -1]
```

The stack stays **decreasing** from bottom to top. That is why it is called *monotonic*.

Why O(n)? Every index is pushed once and popped at most once, even though there is a `while` inside a `for`.

Variants:

| Question | Stack | Condition to pop |
| --- | --- | --- |
| next greater | decreasing | `nums[top] < x` |
| next smaller | increasing | `nums[top] > x` |
| distance (days to wait) | indexes | answer is `i - top` |
| circular list | loop `2 * n` times | push only in the first round |
| largest rectangle | increasing, add a `0` at the end | width from the new top |

## Type 3: stack with a counter

When "equal neighbours" need a count (remove `k` duplicates), each stack item is `[letter, count]`.

## Type 4: stack of (text, number) for nesting

For `3[a2[c]]`: on `[` push what you have so far, on `]` pop and combine.

## Do I need a real stack?

Sometimes a single **counter** is enough. For "minimum additions to make parentheses valid" there is only one kind of bracket, so a number of open brackets does the job.

## Common mistakes

- Popping from an **empty** stack (`IndexError`). Always check `if stack` first.
- Pushing **values** when you need **indexes** (you cannot compute distances or fill the answer list).
- Strict vs not strict: `<` and `<=` change the answer when values are equal.
- Forgetting to check at the **end** that the stack is empty (for brackets).
- Using `list.pop(0)` as a queue: it is O(n). A stack only touches the end.

## Interview corner

**Q: Why is the monotonic stack O(n) with a `while` inside a `for`?**
A: Every item is pushed once and popped at most once, so the total number of operations is at most 2n.

**Q: Why store indexes, not values?**
A: With the index you get the value (`nums[i]`) and also the position, which you need for distances and for the answer array.

**Q: How do you handle a circular list?**
A: Walk the list twice (`i % n`), pushing indexes only in the first round.

**Q: Valid parentheses: time and space?**
A: O(n) time, O(n) space for the stack.

## Summary

- A Python list is a stack: `append`, `pop()`, `stack[-1]`.
- Plain stack: matching, nesting, undo. Check for empty before `pop`.
- Monotonic stack: keep waiting indexes; a new value pops everything it beats. O(n) total.
- Next greater pops while `<`, next smaller pops while `>`.
- Stack items can carry extra info: a count, or `(text, number)`.
- Cheat sheet: `reference/patterns.md`.
