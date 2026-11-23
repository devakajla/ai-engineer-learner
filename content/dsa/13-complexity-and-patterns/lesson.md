---
title: "Complexity & how patterns work"
summary: "Count work with Big-O, read input limits, and learn why every hard problem is an old pattern in disguise."
plan_ids: []
---

Until now you solved problems that just needed to be **correct**. In interviews and contests a correct answer that is too slow still fails. This lesson gives you two tools: **Big-O** (how much work your code does) and the **pattern mindset** (most problems are a few ideas in new clothes).

> Video (Hindi/English mix): the intro video at the top of this page explains Big-O from zero. The code below is Python.

## Why speed matters

A computer does about **10⁸ (100 million) simple steps per second**. Interview sites allow roughly one second. So your code may do about 10⁸ simple operations in total. If the input has 10⁵ items, a double loop does 10¹⁰ steps. That is far too slow.

## Big-O: count the steps, ignore small details

Big-O says how the work **grows** when the input size `n` grows. We keep only the biggest term and drop constants.

```python
def first_item(items):
    return items[0]            # 1 step, any n    -> O(1)

def total(items):
    t = 0
    for x in items:            # n steps          -> O(n)
        t += x
    return t

def all_pairs(items):
    count = 0
    for a in items:            # n times
        for b in items:        # n times each     -> O(n²)
            count += 1
    return count

print(all_pairs([1, 2, 3]))    # -> 9
```

Two loops one after the other are `n + n = 2n`, still **O(n)**. A loop inside a loop multiplies: **O(n²)**.

## Common growth rates

| Name | Looks like | Example |
| --- | --- | --- |
| O(1) | no loop | `items[0]`, `d[key]` |
| O(log n) | halve each step | binary search |
| O(n) | one loop | sum, max, count |
| O(n log n) | sort | `sorted(items)` |
| O(n²) | loop in loop | all pairs |
| O(n³) | three loops | all triplets |
| O(2ⁿ) | all subsets | brute-force subsets |
| O(n!) | all orders | all permutations |

## O(log n): halving

```python
def halving_steps(n):
    steps = 0
    while n > 1:
        n //= 2
        steps += 1
    return steps

print(halving_steps(8))        # -> 3
print(halving_steps(1000000))  # -> 19
```

A million items need only about 20 steps. That is why halving ideas (binary search) are so strong.

## Read the limits first

The input size tells you which complexity is allowed (about 10⁸ steps):

| n up to | Allowed |
| --- | --- |
| 10 | O(n!) |
| 20 | O(2ⁿ) |
| 500 | O(n³) |
| 5 000 | O(n²) |
| 10⁶ | O(n log n) |
| 10⁸ | O(n) |
| more | O(log n) |

Rule of thumb: **look at `n` before you write any code.** If `n` is 10⁵, an O(n²) brute force will time out, so look for something smarter.

## Brute force first, then improve

Always know the slow, obvious answer. It is your baseline and your test oracle.

```python
def has_pair_brute(nums, target):      # O(n²)
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return True
    return False

def has_pair_seen(nums, target):       # O(n), extra space O(n)
    seen = set()
    for x in nums:
        if target - x in seen:
            return True
        seen.add(x)
    return False

print(has_pair_seen([2, 7, 11], 9))    # -> True
```

We traded **space** (a set) for **time**. Sometimes you can get speed with no extra space at all. That is what the next lessons do.

## What is a pattern?

A **pattern** is a reusable way of looking at a problem. "Two Sum on a sorted list", "remove duplicates from a sorted list" and "merge two sorted lists" look different, but all use the same trick: two indexes walking through the data. Learn the trick once, then spot it by its **signals**:

1. What is the **data shape** (sorted array, string, linked list)?
2. What does the **question ask** (pair, triplet, longest, count)?
3. What are the **limits** (does O(n²) fit)?

For every pattern in this track you will get: when to use it, a code template, and 15+ problems from easy to medium.

## Common mistakes

- Starting to code before reading `n`.
- Saying "O(2n)". Write O(n): constants are dropped.
- Forgetting that `sorted()`, `in` on a list, `list.insert(0, x)` and slicing also cost O(n) or more.
- Ignoring space: a set or dict of all items is O(n) extra memory.

## Interview corner

- **Q: What is the time complexity of looking up a key in a dict or set?** O(1) on average, because of hashing.
- **Q: Why do we drop constants and small terms?** Big-O describes growth for large `n`. For huge `n`, `n² + n` behaves like `n²`.
- **Q: What is the cost of `x in some_list` vs `x in some_set`?** O(n) vs O(1) average.
- **Q: n is 10⁵. Is O(n²) fine?** No: 10¹⁰ steps. Aim for O(n log n) or O(n).

## Summary

- About 10⁸ simple steps per second is the budget; check `n` first.
- Big-O keeps the biggest term and drops constants; nested loops multiply.
- Halving gives O(log n); sorting costs O(n log n).
- Brute force is your baseline; improve it with a pattern.
- A pattern = signals (data shape, question, limits) + a template.
- Next: **Two pointers** (`dsa/14-two-pointers`). Reference: `reference/patterns.md`.
