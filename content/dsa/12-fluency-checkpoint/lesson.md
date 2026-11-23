---
title: "Fluency checkpoint"
summary: "No new concepts: six mixed problems and a cheat-sheet of the patterns from this level."
plan_ids: []
---

You have now used loops, math, strings, lists, tuples, sets, dicts and nested data. This lesson adds **nothing new**. It checks that you can combine them under the 5-step routine.

## The routine, one more time

1. Understand the input and output.
2. Work one example by hand.
3. Plan in plain words.
4. Code.
5. Test the edges: empty, one item, repeats, negatives.

## Pattern cheat-sheet

| Pattern | Idea | Where you met it |
| --- | --- | --- |
| Accumulator | running total or product | sum, factorial, running sum |
| Counter | `count += 1` when a condition is true | count vowels |
| Best so far | one variable holds the max/min/answer | biggest, second largest |
| Peel digits | `% 10` then `// 10` | digit sum, reverse number |
| Build a new list | start `[]`, `append` | fizzbuzz, move zeros |
| Two indexes | `i` and `j` walk the data | merge sorted |
| Seen-set | `if x in seen: ... ; seen.add(x)` | has duplicate |
| Counter-dict | `counts[x] = counts.get(x, 0) + 1` | char frequency |
| Group-dict | `groups.setdefault(key, []).append(x)` | group by length |
| Remember-seen | dict from value to index | two sum |
| Sort with key | `sorted(items, key=f)` | rank students |

## How to pick a pattern

Ask these questions:

- "Is there a repeat or a first repeat?" Seen-set.
- "How many times does each thing appear?" Counter-dict.
- "Do I need the biggest or smallest?" Best so far.
- "Do I need to look something up many times?" Dict or set.
- "Are two lists or two ends involved?" Two indexes.

## Common mistakes

- Starting to code before the example is clear.
- Skipping empty input and single-item input.
- Using a list for repeated `in` checks when a set would do.
- Changing the input list when the function should return a new one.

## Summary

- Every problem so far is built from a small set of patterns.
- Naming the pattern is half the solution.
- Next in this track: complexity and real DSA, with these patterns as your base.
- Look up methods in `reference/`.
