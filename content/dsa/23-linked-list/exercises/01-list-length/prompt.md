# Length of a linked list

Write `list_length(head)` that returns the number of nodes. `head` is `None` for an empty list.

```python
list_length(build([4, 5, 6]))    # -> 3
list_length(None)                # -> 0
```

**Think first:** how do you know you reached the end?

**Hint:** pattern *walk the list*: `while node: node = node.next`.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
