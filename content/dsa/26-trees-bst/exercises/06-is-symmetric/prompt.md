# Symmetric tree

A tree is **symmetric** if its left subtree is a mirror image of its right subtree. Write `is_symmetric(root)`. An empty tree is symmetric.

```python
is_symmetric(build([1, 2, 2, 3, 4, 4, 3]))          # -> True
is_symmetric(build([1, 2, 2, None, 3, None, 3]))    # -> False
```

**Think first:** to compare two subtrees `a` and `b` as mirrors, which children of `a` pair with which children of `b`?

**Hint:** pattern *two-node recursion*: `mirror(a, b)`: both `None` -> `True`; one `None` -> `False`; values equal and `mirror(a.left, b.right)` and `mirror(a.right, b.left)`.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
