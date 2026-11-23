# Reverse nodes in groups of k

Write `reverse_k_group(head, k)` that reverses the nodes `k` at a time and returns the head. If fewer than `k` nodes are left at the end, keep them as they are. `k >= 1`.

```python
to_list(reverse_k_group(build([1, 2, 3, 4, 5]), 2))    # -> [2, 1, 4, 3, 5]
to_list(reverse_k_group(build([1, 2, 3, 4, 5]), 3))    # -> [3, 2, 1, 4, 5]
```

**Think first:** for each group, how do you check that `k` nodes exist? Which node links the reversed group to the next one?

**Hint:** pattern *group reversal with a dummy*: find the k-th node from `group_prev`; reverse the group; reconnect `group_prev.next` to the old k-th node and move `group_prev` to the old first node.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
