# Search in a BST

`root` is a binary search tree. Write `contains(root, val)` that returns `True` if `val` is in the tree. It should take O(height), not O(n).

```python
t = build([4, 2, 7, 1, 3])
contains(t, 2)    # -> True
contains(t, 5)    # -> False
```

**Think first:** at a node, if `val` is smaller, can it be in the right subtree?

**Hint:** pattern *BST walk*: loop `while node:`; equal -> `True`; smaller -> `node = node.left`; bigger -> `node = node.right`.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
