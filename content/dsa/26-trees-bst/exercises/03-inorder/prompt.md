# Inorder traversal

Inorder visits **left subtree, node, right subtree**. Write `inorder(root)` that returns the values as a list. (For a BST this gives the values in sorted order.)

```python
inorder(build([1, None, 2, 3]))    # -> [1, 3, 2]
inorder(build([2, 1, 3]))          # -> [1, 2, 3]
```

**Think first:** where does the current value go between the two recursive results?

**Hint:** pattern *DFS recursion*: `inorder(left) + [root.val] + inorder(right)`.

> `TreeNode` is given in `starter.py`. You only use `.val`, `.left` and `.right`. (You will learn classes in Python lesson 19.) In the tests a tree is built from a level-order list like `[1, 2, 3, None, 4]` (`None` = no node).
