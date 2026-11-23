# Invert a binary tree

Write `invert_tree(root)` that swaps the left and right child of **every** node and returns the root.

```python
invert_tree(build([4, 2, 7, 1, 3, 6, 9]))    # -> tree [4, 7, 2, 9, 6, 3, 1]; its preorder is [4, 7, 9, 6, 2, 3, 1]
invert_tree(None)                                         # -> None
```

**Think first:** inverting a tree means: swap the two children, then invert each child. What is the base case?

**Hint:** pattern *recursive swap*: `root.left, root.right = invert_tree(root.right), invert_tree(root.left)`.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
