# Rotate a list to the right

Write `rotate_right(head, k)` that moves the last `k` nodes to the front (`k >= 0`, can be bigger than the length). Return the new head.

```python
to_list(rotate_right(build([1, 2, 3, 4, 5]), 2))    # -> [4, 5, 1, 2, 3]
to_list(rotate_right(build([1, 2]), 5))             # -> [2, 1]
```

**Think first:** rotating by the length changes nothing. What is the real `k`? Where must the list be cut?

**Hint:** pattern *make a ring, then cut*: count `n` and find the tail; `k %= n`; link `tail.next = head`; walk `n - k - 1` steps to the new tail; cut after it.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
