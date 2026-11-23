# Two sum in a BST

`root` is a binary search tree with different values. Write `find_target(root, k)` that returns `True` if two **different nodes** have values that add up to `k`.

```python
t = build([5, 3, 6, 2, 4, None, 7])
find_target(t, 9)     # -> True   (2 + 7)
find_target(t, 28)    # -> False
```

**Think first:** the inorder list of a BST is sorted. Which earlier pattern works on a sorted list?

**Hint:** pattern *inorder + two pointers*: collect the inorder values, then `lo`, `hi` pointers move inward (or use a `seen` set while walking).

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
