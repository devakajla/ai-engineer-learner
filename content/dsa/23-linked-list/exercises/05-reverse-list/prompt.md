# Reverse a linked list

Write `reverse_list(head)` that reverses the list **in place** (change the `.next` links) and returns the new head.

```python
to_list(reverse_list(build([1, 2, 3])))    # -> [3, 2, 1]
reverse_list(None)                         # -> None
```

**Think first:** to point a node backward you must remember the next node first. What do you keep while walking?

**Hint:** pattern *three pointers*: `prev = None`; loop: `nxt = cur.next; cur.next = prev; prev = cur; cur = nxt`. Return `prev`.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
