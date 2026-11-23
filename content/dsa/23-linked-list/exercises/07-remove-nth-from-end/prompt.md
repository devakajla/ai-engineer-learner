# Remove the n-th node from the end

Write `remove_nth_from_end(head, n)` that removes the n-th node from the end (`n = 1` is the last) and returns the head. `n` is always valid.

```python
to_list(remove_nth_from_end(build([1, 2, 3, 4, 5]), 2))    # -> [1, 2, 3, 5]
to_list(remove_nth_from_end(build([1]), 1))                # -> []
```

**Think first:** to delete a node you need the node **before** it. What if the node to delete is the head?

**Hint:** pattern *dummy node + gap*: `dummy = ListNode(0, head)`; move `fast` n+1 steps from `dummy`; then move both; `slow.next = slow.next.next`. Return `dummy.next`.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
