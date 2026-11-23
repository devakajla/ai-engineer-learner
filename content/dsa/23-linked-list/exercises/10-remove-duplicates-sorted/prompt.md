# Remove duplicates from a sorted list

The list is sorted. Write `remove_duplicates(head)` that keeps **one** node for each value and returns the head.

```python
to_list(remove_duplicates(build([1, 1, 2, 3, 3])))    # -> [1, 2, 3]
to_list(remove_duplicates(build([2, 2, 2])))          # -> [2]
```

**Think first:** equal values are neighbours. When the next node has the same value, what do you skip?

**Hint:** pattern *walk and skip*: `while cur and cur.next:` if equal, `cur.next = cur.next.next` (do not move), else `cur = cur.next`.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
