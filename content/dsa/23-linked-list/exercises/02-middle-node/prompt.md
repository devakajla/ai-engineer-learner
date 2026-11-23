# Middle of a linked list

Write `middle_node(head)` that returns the **middle node**. For an even length return the **second** of the two middles. Return `None` for an empty list.

```python
middle_node(build([1, 2, 3, 4, 5]))    # -> the node with val 3
middle_node(build([1, 2, 3, 4]))       # -> the node with val 3
```

**Think first:** you cannot ask for the length in one pass. Can two walkers, one twice as fast, help?

**Hint:** pattern *slow and fast pointers*: `slow` moves 1, `fast` moves 2; stop when `fast` or `fast.next` is `None`.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
