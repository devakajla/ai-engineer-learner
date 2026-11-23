# N-th value from the end

Write `nth_from_end(head, n)` that returns the **value** of the n-th node counted from the end (`n = 1` is the last node). `n` is always valid. One pass, no length counting.

```python
nth_from_end(build([1, 2, 3, 4, 5]), 2)    # -> 4
nth_from_end(build([9]), 1)                # -> 9
```

**Think first:** if one pointer is already `n` steps ahead, where is the other when the first one falls off the end?

**Hint:** pattern *gap of n*: move `fast` n steps; then move both until `fast` is `None`; `slow` is the answer.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
