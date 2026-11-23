---
title: "Intervals"
summary: "Sort intervals by start, then sweep once to merge, insert, intersect or count overlaps."
plan_ids: []
---

An **interval** is a pair `[start, end]`: a meeting, a booking, a range of numbers. Questions ask to merge them, find overlaps, count how many run at once, or find free time.

The one habit that makes almost all of them easy: **sort by start first**. After sorting, an interval can only overlap the ones right next to it, so one pass is enough. Cost: O(n log n) for the sort, then O(n).

> Watch the intro video first. Exercises 01 to 05 have video segments.

## When to think "intervals"

- Pairs like `[start, end]`, meetings, ranges, bookings.
- Words: merge, overlap, insert, conflict, free time, minimum rooms, cover.

## Do two intervals overlap?

For `[a, b]` and `[c, d]` (closed), they overlap when `a <= d and c <= b`. Always ask: **does touching count?** (`[1, 4]` and `[4, 5]`)

- Closed intervals: touching **merges** (`<=`).
- Half-open `[start, end)` meetings: touching is **fine** (`<`).

State the rule before you code, and test the touching case.

## Pattern 1: sort + merge

```python
def merge_intervals(intervals):
    merged = []
    for start, end in sorted(intervals):      # sorts by start, then end
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)   # overlap: extend
        else:
            merged.append([start, end])               # gap: new interval
    return merged

print(merge_intervals([[1, 3], [2, 6], [8, 10]]))   # -> [[1, 6], [8, 10]]
```

Take the **max** of the ends: the new interval may sit inside the last one.

## Pattern 2: already sorted -> three phases (insert)

When the list is sorted and disjoint, no sorting is needed:

1. copy the intervals that end **before** `new` starts,
2. merge the ones that overlap `new` (min of starts, max of ends),
3. copy the rest.

## Pattern 3: two sorted lists, two pointers (intersection)

The overlap of two intervals is `[max(starts), min(ends)]`, valid if `lo <= hi`. Then **move the pointer of the interval that ends first**.

## Pattern 4: sweep line (rooms, max overlap)

Split every interval into two events: `+1` at the start, `-1` at the end. Sort the events and keep a running count. The maximum of the count is the most intervals running at once.

```python
def min_meeting_rooms(meetings):
    starts = sorted(m[0] for m in meetings)
    ends = sorted(m[1] for m in meetings)
    rooms = j = 0
    for s in starts:
        if s >= ends[j]:
            j += 1            # a room was freed
        else:
            rooms += 1        # need one more room
    return rooms

print(min_meeting_rooms([[0, 30], [5, 10], [15, 20]]))   # -> 2
```

## Pattern 5: greedy by END

"Keep the most intervals" or "fewest arrows": sort by **end** and always take the interval that ends first. It leaves the most room for the rest. Python trick without `lambda`: sort tuples `(end, start)`.

```python
for end, start in sorted((e, s) for s, e in intervals):
    ...
```

## Pattern 6: free time and covering

Walk sorted intervals with a `cursor` meaning "covered up to here". A gap exists when `start > cursor`. Then `cursor = max(cursor, end)`.

## Common mistakes

- Not sorting first.
- Replacing the end instead of taking `max(end, last_end)` (misses the "inside another" case).
- Wrong touching rule (`<` vs `<=`). Decide it from the problem.
- Changing the input list while merging (copy the intervals).
- Forgetting the last gap or the last interval after the loop.
- Sorting by start when the problem needs greedy by end.

## Interview corner

**Q: Why sort by start in merge intervals?**
A: Then any interval that overlaps the current merged one is next in line, so a single pass with the last merged interval is enough.

**Q: Time complexity?**
A: O(n log n) for sorting, O(n) for the pass. If the input is already sorted, O(n).

**Q: Minimum meeting rooms: another way?**
A: A min-heap of end times, or the two sorted lists method. Both are O(n log n).

**Q: Closed or half-open?**
A: Ask the interviewer. It changes `<` and `<=`, and often the answer on boundary cases.

## Summary

- Intervals: sort by start, then one pass. O(n log n).
- Overlap test: `a <= d and c <= b`. Decide how touching counts.
- Merge: extend with `max(end)`. Insert: three phases. Intersect: two pointers. Rooms: sweep with `+1/-1`.
- Greedy by end for "keep most / fewest arrows".
- Cheat sheet: `reference/patterns.md`.
