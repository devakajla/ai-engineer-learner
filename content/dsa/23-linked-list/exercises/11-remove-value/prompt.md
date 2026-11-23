# Remove all nodes with a value

Write `remove_value(head, val)` that removes **every** node whose value equals `val` and returns the new head.

```python
to_list(remove_value(build([1, 2, 6, 3, 6]), 6))    # -> [1, 2, 3]
to_list(remove_value(build([7, 7]), 7))             # -> []
```

**Think first:** the head itself may need to go. How does a dummy node remove that special case?

**Hint:** pattern *dummy head*: `prev = dummy`; if `prev.next.val == val` then `prev.next = prev.next.next` else `prev = prev.next`.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
