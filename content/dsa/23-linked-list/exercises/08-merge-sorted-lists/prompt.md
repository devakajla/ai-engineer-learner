# Merge two sorted lists

Write `merge_sorted(a, b)` that merges two sorted linked lists into one sorted list by **relinking the existing nodes**. Return the head. When values are equal, take from `a` first.

```python
to_list(merge_sorted(build([1, 3, 5]), build([2, 4])))    # -> [1, 2, 3, 4, 5]
to_list(merge_sorted(None, build([1])))                   # -> [1]
```

**Think first:** how do you avoid a special case for the first node?

**Hint:** pattern *dummy head + tail*: compare `a.val` and `b.val`, attach the smaller to `tail`, move that list forward; at the end attach the rest.

> `ListNode` is given in `starter.py`. You only use `.val` and `.next`. (You will learn classes in Python lesson 19.)
