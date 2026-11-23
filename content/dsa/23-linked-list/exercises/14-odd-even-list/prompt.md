# Odd-even list

Write `odd_even_list(head)` that groups all nodes at **odd positions** (1st, 3rd, ...) first, then all nodes at **even positions** (2nd, 4th, ...). Keep the order inside each group. Change links only; return the head.

```python
to_list(odd_even_list(build([1, 2, 3, 4, 5])))    # -> [1, 3, 5, 2, 4]
to_list(odd_even_list(build([2, 1, 3, 5, 6])))    # -> [2, 3, 6, 1, 5]
```

**Think first:** build two chains at the same time. What must you remember so you can join them?

**Hint:** pattern *two chains*: `odd = head`, `even = head.next`, `even_head = even`; relink `odd.next = even.next`, `even.next = odd.next`...; at the end `odd.next = even_head`.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
