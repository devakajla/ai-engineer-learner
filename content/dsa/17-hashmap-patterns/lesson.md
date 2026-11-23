---
title: "Hashmap patterns"
summary: "Use a dict or set to remember what you saw, so one pass replaces a nested loop."
plan_ids: []
---

A **hashmap** (a Python `dict`) and a **hash set** (a `set`) find a key in O(1) on average. That one fact turns many O(n²) loops into O(n): instead of searching the list again, you **look it up**.

> Watch the intro video first. The second video (4 questions) is attached to the first four exercises.

## When to think "hashmap"

- "How many times does it appear?" -> counts.
- "Have I seen this before?" / "is there a pair with ...?" -> seen-set or seen-dict.
- "Group things that share a property" -> dict of lists.
- "Match one thing to another" -> two dicts.
- You are about to write a loop **inside** a loop just to find a value.

## Pattern 1: counter-dict

```python
def count_letters(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    return counts

print(count_letters("banana"))   # -> {'b': 1, 'a': 3, 'n': 2}
```

Almost every string question starts with "count the letters". Variants: frequency of a **need** list vs an **available** list (ransom note, balloons), pairs for palindromes (`n // 2 * 2`).

## Pattern 2: seen-set and seen-dict (Two Sum)

For each `x`, the partner is `target - x`. Look it up in what you have **already seen**.

```python
def two_sum(nums, target):
    index_of = {}
    for j, x in enumerate(nums):
        need = target - x
        if need in index_of:
            return [index_of[need], j]
        index_of[x] = j          # store after checking, so x is not used twice
    return []

print(two_sum([2, 7, 11, 15], 9))   # -> [0, 1]
```

O(n) instead of O(n²). The trade is **memory**: O(n) extra space.

## Pattern 3: group by key

Choose a **key** that is equal for items you want together (anagrams: the sorted letters).

```python
groups = {}
for word in ["eat", "tea", "tan"]:
    key = "".join(sorted(word))
    groups.setdefault(key, []).append(word)
print(list(groups.values()))     # -> [['eat', 'tea'], ['tan']]
```

## Pattern 4: two dicts for a one-to-one mapping

"Each letter maps to exactly one letter **and** no two letters share one" needs `a -> b` and `b -> a`.

## Pattern 5: set for O(1) lookup

Put everything in a `set`, then only start work where it makes sense (longest consecutive run: start only when `x - 1` is missing).

## Pattern 6: meet in the middle with pair sums

For four lists, store all sums of two lists in a dict and look up the other two. O(n²) instead of O(n⁴).

## Dict tools you need

| Tool | Meaning |
| --- | --- |
| `d.get(k, 0)` | value or a default, no error |
| `d.setdefault(k, [])` | create the empty list if the key is new |
| `k in d` | O(1) check |
| `del d[k]` | remove a key |
| `d.items()` / `d.values()` | loop over pairs / values |

## Common mistakes

- Putting `x` in the dict **before** checking for the partner (a number pairs with itself).
- Using a `list` for "have I seen it" (`x in list` is O(n), the loop becomes O(n²)).
- Using a mutable key (a list can not be a key; use a tuple or a string).
- Forgetting empty input, and that keys must be hashable.
- Counting a unique pair twice (`(1, 3)` and `(3, 1)`).

## Interview corner

**Q: Time and space of a hashmap solution?**
A: Usually O(n) time and O(n) space. It trades memory for speed.

**Q: Is dict lookup always O(1)?**
A: On average. In the worst case (many collisions) it can be O(n), but that is rare.

**Q: Hashmap or sorting?**
A: Hashmap is O(n) but uses extra space. Sorting is O(n log n) but can be in place, and helps with two pointers.

**Q: What can be a dict key?**
A: Any hashable (immutable) value: numbers, strings, tuples. Not lists, dicts or sets.

## Summary

- A dict/set turns "search again" into one lookup: O(n) overall, O(n) memory.
- Patterns: counter-dict, seen-set/dict, group by key, two dicts, set lookup, pair sums.
- Check the partner **before** you store the current item.
- Common prefix-sum uses of dicts are in lesson 16. Cheat sheet: `reference/patterns.md`.
