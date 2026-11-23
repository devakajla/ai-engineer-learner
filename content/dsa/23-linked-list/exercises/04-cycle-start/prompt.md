# Where does the cycle start?

Write `cycle_start(head)` that returns the **node** where the cycle begins, or `None` if there is no cycle. O(1) extra space.

```python
head, nodes = build_cycle([3, 2, 0, -4], 1)
cycle_start(head) is nodes[1]    # -> True
cycle_start(build([1, 2]))       # -> None
```

**Think first:** after slow and fast meet inside the cycle, what happens if you start a second pointer from `head` and move both by 1?

**Hint:** pattern *Floyd phase 2*: find the meeting node; then move one pointer from `head` and one from the meeting node, 1 step each; they meet at the cycle start.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
