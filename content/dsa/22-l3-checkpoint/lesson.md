---
title: "Level 3 checkpoint"
summary: "Mixed revision: pick the right pattern for each problem from Level 3."
plan_ids: []
---

You learned eight patterns in Level 3. In real problems nobody tells you which one to use. This checkpoint mixes them. For each problem, **name the pattern first**, then code.

## Pattern chooser

| You see | Try |
| --- | --- |
| Sorted list, pair or triple with a target | Two pointers |
| "Longest or shortest subarray or substring" with a rule, non-negative numbers | Sliding window |
| Sum of a range, or subarrays with a sum rule (negatives allowed) | Prefix sum + dict |
| Count, group, or "have I seen this" | Hashmap or set |
| Brackets, "next greater", undo-like behaviour | Stack, monotonic stack |
| Best subarray sum, extend or restart | Kadane |
| Pairs `[start, end]`, overlaps | Sort + sweep |
| Sorted data, or "smallest X that works" | Binary search |

## How to use this level

1. Read the problem. Write the pattern name on paper before coding.
2. Do the 5-step routine from lesson 01: understand, example by hand, plan, code, test edges.
3. If the tests fail, find which edge case broke it. Do not guess.

## Common mistakes

- Reaching for a nested loop first. Ask which pattern removes the inner loop.
- Using a sliding window when numbers can be negative (use prefix sum + dict).
- Forgetting empty input and one-item input.

## Interview corner

**Q: How do you choose between sliding window and prefix sum?**
A: Window needs the sum to move in one direction (non-negative numbers). With negatives use prefix sums and a dict.

**Q: When is binary search possible without a sorted list?**
A: When a yes/no check on a guess flips once, like capacity or speed problems.

## Summary

- Name the pattern, then code.
- Revise the cheat sheet in `reference/patterns.md`.
- Level 4 (lessons 23 and on) starts after this checkpoint.
