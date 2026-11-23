# Length of the cycle

Write `cycle_length(head)` that returns the number of nodes **inside** the cycle, or `0` if there is no cycle.

```python
cycle_length(build_cycle([1, 2, 3, 4, 5], 2)[0])    # -> 3    (3, 4, 5 form the loop)
cycle_length(build([1, 2, 3]))                      # -> 0
```

**Think first:** once slow and fast meet, they are inside the loop. How can you count its nodes from there?

**Hint:** pattern *Floyd + count*: after the meeting node, walk one pointer around until it returns to the meeting node, counting steps.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
