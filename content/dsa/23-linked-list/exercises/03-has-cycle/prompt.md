# Does the list have a cycle?

In some lists the last node points back to an earlier node, so walking never ends. Write `has_cycle(head)` that returns `True` if there is a cycle. Use O(1) extra space.

```python
has_cycle(build_cycle([1, 2, 3, 4], 1)[0])    # -> True   (4 points back to 2)
has_cycle(build([1, 2, 3]))                   # -> False
```

**Think first:** on a circular track a fast runner always catches a slow one. What do you compare?

**Hint:** pattern *slow and fast pointers (Floyd)*: move `slow` by 1 and `fast` by 2; if they ever point to the same node, there is a cycle; if `fast` reaches `None`, there is none.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
