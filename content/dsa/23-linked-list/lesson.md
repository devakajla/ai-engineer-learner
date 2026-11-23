---
title: "Linked list"
summary: "Walk and relink nodes: slow/fast pointers, reversal, dummy head, rotation and groups."
plan_ids: []
---

A **linked list** is a chain of nodes. Each node holds a value (`.val`) and a link to the next node (`.next`). The last node has `.next = None`. You cannot jump to index 5: you must walk from the head. In return, inserting or removing a node needs no shifting.

> In these exercises `ListNode` is given as ready code in `starter.py`. You only use `.val` and `.next`. You will learn classes in Python lesson 19.

> Watch the intro video first. Some exercises have video segments.

## Basics

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

head = ListNode(1, ListNode(2, ListNode(3)))   # 1 -> 2 -> 3

node = head
while node:                 # walk the list
    print(node.val)         # -> 1, then 2, then 3
    node = node.next
```

Rules that save you from bugs:

- Walking is `while node:`. Reading `node.next.val` needs `node.next` to be not `None`.
- Before you change `node.next`, **save the old next** in a variable.
- Draw boxes and arrows on paper for every problem.

## Pattern 1: slow and fast pointers

`slow` moves 1 step, `fast` moves 2.

- When `fast` reaches the end, `slow` is at the **middle**.
- If there is a cycle, `fast` catches `slow` inside it (Floyd).

```python
slow = fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
# slow is the middle (the second middle for even length)
```

**Cycle start:** after they meet, put one pointer at `head`; move both 1 step at a time; they meet at the cycle start.

## Pattern 2: gap of n

Move `fast` n steps ahead, then move both. When `fast` falls off the end, `slow` is n from the end.

## Pattern 3: dummy head

Create `dummy = ListNode(0, head)`. Now the head is not a special case when you delete or insert. Return `dummy.next`.

## Pattern 4: reversal

```python
prev = None
cur = head
while cur:
    nxt = cur.next      # save
    cur.next = prev     # turn the arrow
    prev = cur
    cur = nxt
# prev is the new head
```

Reversal is the building block for palindrome check, k-group reversal and "reorder" problems.

## Pattern 5: rotate and groups

- Rotate: join the tail to the head to make a ring, then cut at the right place (`k %= n`).
- k-group: for each group, check that k nodes exist, reverse the group, reconnect both ends.

## Common mistakes

- Losing the rest of the list because `.next` was overwritten before saving it.
- `None` errors: `fast.next.next` without checking `fast` and `fast.next`.
- Forgetting empty list and one-node list.
- Returning the old head after reversing.
- Infinite loops when a cycle exists and you walk with `while node`.

## Interview corner

**Q: How do you find the middle in one pass?**
A: Slow and fast pointers. Fast moves two steps for each step of slow.

**Q: Why does Floyd's cycle detection work?**
A: Inside a cycle the gap between fast and slow shrinks by 1 each step, so they must meet.

**Q: Reverse a list in place: time and space?**
A: O(n) time, O(1) space.

**Q: Why use a dummy node?**
A: It removes the special case when the head changes (delete head, merge, insert at front).

## Summary

- Walk with `while node`; save `.next` before changing it.
- Slow/fast: middle and cycle. Gap of n: n-th from the end. Dummy head: safe edits. Three pointers: reverse.
- Cheat sheet: `reference/patterns.md`.
